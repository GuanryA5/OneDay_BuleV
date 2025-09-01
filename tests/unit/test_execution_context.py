# -*- coding: utf-8 -*-
import asyncio
import time

import pytest

from bluev.core.execution_context import ExecutionContext


@pytest.mark.asyncio
async def test_callbacks_and_status_flow():
    ctx = ExecutionContext(workflow_id="wf-cb")

    events = []

    def on_start(c, **kw):
        events.append(("start", bool(c.is_running)))

    def on_complete(c, **kw):
        events.append(("complete", not c.is_running))

    def on_error(c, **kw):
        events.append(("error", True))

    ctx.add_callback("workflow_start", on_start)
    ctx.add_callback("workflow_complete", on_complete)
    ctx.add_callback("workflow_error", on_error)

    # start / finish
    ctx.start_execution()
    assert ctx.is_running is True

    ctx.finish_execution(success=True)
    assert ctx.is_running is False

    # callback results
    # 注意：目前 start/finish 不会自动触发 callbacks，这里仅验证 add 与生命周期变量
    assert events == [("start", True), ("complete", True)]  # 手动调用未触发 on_error


def test_timeout_check():
    ctx = ExecutionContext(workflow_id="wf-time", max_execution_time=0.01)
    ctx.start_execution()
    time.sleep(0.02)
    assert ctx.check_timeout() is True


@pytest.mark.asyncio
async def test_pause_resume_wait():
    ctx = ExecutionContext(workflow_id="wf-pause")
    ctx.start_execution()

    ctx.pause_execution()
    assert ctx.is_paused is True

    async def resume_later():
        await asyncio.sleep(0.05)
        ctx.resume_execution()

    t = asyncio.create_task(resume_later())

    start = time.time()
    await ctx.wait_if_paused()
    elapsed = time.time() - start

    assert elapsed >= 0.05
    assert ctx.is_paused is False

    t.cancel()
