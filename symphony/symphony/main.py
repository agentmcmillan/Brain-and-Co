"""Symphony entry point — CLI mode or API server mode."""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys

import uvicorn

from symphony.api.server import create_app
from symphony.config import load_config
from symphony.scheduler.dispatcher import Dispatcher
from symphony.scheduler.state_machine import Task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("symphony")


async def run_single_task(args: argparse.Namespace) -> None:
    """Run a single task and exit (CLI mode)."""
    config = load_config(args.config)
    dispatcher = Dispatcher(config)

    task = Task(
        title=args.title or args.task[:60],
        prompt=args.task,
        repo_url=args.repo or "",
        branch=args.branch or "main",
        source="manual",
        max_turns=args.max_turns,
        timeout_minutes=args.timeout,
    )

    logger.info("Running single task: %s", task.title)
    result = await dispatcher.run_single(task)

    logger.info("Result: %s", result.status.value)
    if result.error:
        logger.error("Error: %s", result.error)

    logger.info(
        "Stats: tokens=%d+%d, cost=$%.4f, elapsed=%ss",
        result.tokens_in,
        result.tokens_out,
        result.cost_usd,
        f"{result.elapsed_seconds:.0f}" if result.elapsed_seconds else "?",
    )

    await dispatcher.shutdown()
    sys.exit(0 if result.status.value == "SUCCESS" else 1)


async def run_server(args: argparse.Namespace) -> None:
    """Run the dispatcher loop + API server."""
    config = load_config(args.config)
    dispatcher = Dispatcher(config)

    # Graceful shutdown on SIGINT/SIGTERM
    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("Shutdown signal received")
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    # Start the dispatch loop
    dispatch_task = asyncio.create_task(dispatcher.run_forever(), name="dispatcher")

    # Start the API server
    app = create_app(dispatcher, api_token=config.server.api_token)
    server_config = uvicorn.Config(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level="info",
    )
    server = uvicorn.Server(server_config)
    server_task = asyncio.create_task(server.serve(), name="api-server")

    logger.info("Symphony running — API at http://%s:%d", config.server.host, config.server.port)

    # Wait for shutdown signal
    await shutdown_event.wait()

    # Cleanup
    server.should_exit = True
    await dispatcher.shutdown()
    dispatch_task.cancel()
    server_task.cancel()

    try:
        await asyncio.gather(dispatch_task, server_task, return_exceptions=True)
    except asyncio.CancelledError:
        pass

    logger.info("Symphony stopped")


def main() -> None:
    parser = argparse.ArgumentParser(description="Symphony — autonomous agent orchestrator")
    parser.add_argument("--config", default="symphony.yaml", help="Config file path")

    sub = parser.add_subparsers(dest="command")

    # CLI mode: run a single task
    run_parser = sub.add_parser("run", help="Run a single task")
    run_parser.add_argument("--task", required=True, help="Task prompt")
    run_parser.add_argument("--repo", help="Git repository URL")
    run_parser.add_argument("--branch", default="main", help="Branch to clone")
    run_parser.add_argument("--title", help="Task title")
    run_parser.add_argument("--max-turns", type=int, default=25, help="Max Claude turns")
    run_parser.add_argument("--timeout", type=int, default=30, help="Timeout in minutes")

    # Server mode: dispatch loop + API
    sub.add_parser("serve", help="Run the dispatch loop and API server")

    args = parser.parse_args()

    if args.command == "run":
        asyncio.run(run_single_task(args))
    elif args.command == "serve":
        asyncio.run(run_server(args))
    else:
        # Default to serve mode
        args.command = "serve"
        asyncio.run(run_server(args))


if __name__ == "__main__":
    main()
