"""Wire-level regression tests against the real stdio server (no HTTP service needed)."""

import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import contextmanager

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODERN = "2026-07-28"
TOOLS = {
    "read_xmind_file", "create_mind_map", "analyze_mind_map",
    "convert_to_xmind", "list_xmind_files", "translate_xmind_titles",
}


@contextmanager
def running_server(flags, output_dir, *, command=None):
    # stderr is separate: any startup text on stdout must fail JSON decoding.
    with tempfile.TemporaryFile(mode="w+t") as errors:
        process = subprocess.Popen(
            [*(command or [sys.executable, "-m", "xmind_mcp"]), *flags,
             "--default-output-dir", str(output_dir)],
            cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=errors, text=True, encoding="utf-8", bufsize=1,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        responses = queue.Queue()

        def read_lines():
            for line in process.stdout:
                responses.put(line)
            responses.put(None)

        reader = threading.Thread(target=read_lines, daemon=True)
        reader.start()
        sequence = 0

        def rpc(method, params=None, version=None, notification=False):
            nonlocal sequence
            sequence += 1
            params = dict(params or {})
            if version:
                params["_meta"] = {
                    "io.modelcontextprotocol/protocolVersion": version,
                    "io.modelcontextprotocol/clientInfo": {
                        "name": "xmind-protocol-test", "version": "1.0.0",
                    },
                    "io.modelcontextprotocol/clientCapabilities": {},
                }
            message = {"jsonrpc": "2.0", "method": method, "params": params}
            if not notification:
                message["id"] = sequence
            process.stdin.write(json.dumps(message) + "\n")
            process.stdin.flush()
            if notification:
                return None
            deadline = time.monotonic() + 20
            while True:
                try:
                    line = responses.get(timeout=max(0.01, deadline - time.monotonic()))
                except queue.Empty:
                    pytest.fail(f"Timed out waiting for {method}")
                if line is None:
                    errors.seek(0)
                    pytest.fail(f"Server closed stdout: {errors.read()}")
                response = json.loads(line)
                assert response["jsonrpc"] == "2.0"
                if response.get("id") == sequence:
                    return response
                assert "id" not in response, response

        try:
            yield rpc
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            reader.join(timeout=5)
            process.stdout.close()


def tool_data(rpc, name, arguments, version):
    response = rpc("tools/call", {"name": name, "arguments": arguments}, version)
    assert "error" not in response, response
    result = response["result"]
    assert not result.get("isError"), result
    return json.loads(result["content"][0]["text"])


@pytest.mark.parametrize("flags", [[], ["--mode", "fastmcp"], ["--mode", "stdio"], ["--stdio"], ["--debug"]])
@pytest.mark.parametrize("version", [MODERN, "2025-11-25", "2024-11-05"])
def test_stdio_protocol_and_tools(flags, version, tmp_path):
    with running_server(flags, tmp_path) as rpc:
        if version == MODERN:
            discovered = rpc("server/discover", version=version)
            assert "error" not in discovered, discovered
            assert MODERN in discovered["result"]["supportedVersions"]
            request_version = version
        else:
            initialized = rpc("initialize", {
                "protocolVersion": version, "capabilities": {},
                "clientInfo": {"name": "legacy-client", "version": "1.0.0"},
            })
            assert initialized["result"]["protocolVersion"] == version
            assert initialized["result"]["serverInfo"]["version"]
            rpc("notifications/initialized", notification=True)
            request_version = None

        listing = rpc("tools/list", version=request_version)
        assert "error" not in listing, listing
        tools = listing["result"]["tools"]
        assert {tool["name"] for tool in tools} == TOOLS
        for tool in tools:
            assert "ctx" not in tool["inputSchema"].get("properties", {})

        created = tool_data(rpc, "create_mind_map", {
            "title": "协议兼容测试",
            "topics_json": json.dumps([{"title": "主题", "topics": [{"title": "子主题"}]}]),
        }, request_version)
        assert created["status"] == "success", created
        output = tmp_path / created["data"]["filename"]
        assert output.is_file()
        for name in ("read_xmind_file", "analyze_mind_map"):
            result = tool_data(rpc, name, {"file_path": str(output)}, request_version)
            assert result["status"] == "success", result
        listed = tool_data(rpc, "list_xmind_files", {"directory": str(tmp_path)}, request_version)
        assert listed["status"] == "success", listed

        converted = tool_data(rpc, "convert_to_xmind", {
            "source_file": str(ROOT / "examples/test_markdown.md"),
            "output_file": str(tmp_path / "converted.xmind"),
        }, request_version)
        assert converted["status"] == "success", converted
        assert (tmp_path / "converted.xmind").is_file()
        invalid = tool_data(rpc, "convert_to_xmind", {"source_filepath": "relative.md"}, request_version)
        assert invalid["status"] == "error", invalid
        bad_arguments = rpc("tools/call", {"name": "read_xmind_file", "arguments": {}}, request_version)
        assert "error" in bad_arguments or bad_arguments["result"].get("isError"), bad_arguments


def test_modern_version_rejection_and_direct_request(tmp_path):
    with running_server([], tmp_path) as rpc:
        unsupported = rpc("tools/list", version="1900-01-01")
        assert unsupported["error"]["code"] == -32022
        assert MODERN in unsupported["error"]["data"]["supported"]
        # Modern calls work without initialize or even server/discover.
        listing = rpc("tools/list", version=MODERN)
        assert {t["name"] for t in listing["result"]["tools"]} == TOOLS


@pytest.mark.parametrize("entry", ["xmind-mcp", "xmind-mcp-server"])
def test_installed_console_entry_point(entry, tmp_path):
    executable = Path(sys.executable).parent / (entry + (".exe" if os.name == "nt" else ""))
    assert executable.is_file(), "Install the project with its test extra before running the suite"
    with running_server(["--stdio"], tmp_path, command=[str(executable)]) as rpc:
        listing = rpc("tools/list", version=MODERN)
        assert {tool["name"] for tool in listing["result"]["tools"]} == TOOLS
        created = tool_data(rpc, "create_mind_map", {"title": "console", "topics_json": "[]"}, MODERN)
        assert created["status"] == "success", created
        assert (tmp_path / "console.xmind").is_file()
