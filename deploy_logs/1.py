17/05/2025, 20:28:07 Using langgraph_runtime_postgres
17/05/2025, 20:28:07 Using auth of type=langsmith
17/05/2025, 20:28:07 Started server process [1]
17/05/2025, 20:28:07 Waiting for application startup.
17/05/2025, 20:28:07 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:28:07 Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 692, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
    await database.start_pool()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
    await migrate_vector_index()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
    lg_store.set_store_config(config_)
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
    _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
    _check_pkg(pkg)
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
    raise ImportError(
ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`

17/05/2025, 20:28:07 Application startup failed. Exiting.
17/05/2025, 20:28:47 2025-05-17 18:28:47 [info     ] Using langgraph_runtime_postgres
17/05/2025, 20:28:47 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:28:47 Health server started at http://0.0.0.0:8000
17/05/2025, 20:28:47 Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/api/langgraph_api/queue_entrypoint.py", line 75, in <module>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
17/05/2025, 20:28:47     return runner.run(main)
17/05/2025, 20:28:47            ^^^^^^^^^^^^^^^^
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
17/05/2025, 20:28:47     return self._loop.run_until_complete(task)
17/05/2025, 20:28:47            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:28:47   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
17/05/2025, 20:28:47   File "/api/langgraph_api/queue_entrypoint.py", line 57, in entrypoint
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
17/05/2025, 20:28:47     return await anext(self.gen)
17/05/2025, 20:28:47            ^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
17/05/2025, 20:28:47     await database.start_pool()
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
17/05/2025, 20:28:47     await migrate_vector_index()
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
17/05/2025, 20:28:47     lg_store.set_store_config(config_)
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
17/05/2025, 20:28:47     _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
17/05/2025, 20:28:47                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:28:47   File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
17/05/2025, 20:28:47     _check_pkg(pkg)
17/05/2025, 20:28:47   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
17/05/2025, 20:28:47     raise ImportError(
17/05/2025, 20:28:47 ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`
17/05/2025, 20:33:20 Using langgraph_runtime_postgres
17/05/2025, 20:33:20 Using auth of type=langsmith
17/05/2025, 20:33:20 Started server process [1]
17/05/2025, 20:33:20 Waiting for application startup.
17/05/2025, 20:33:20 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:33:20 Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 692, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
    await database.start_pool()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
    await migrate_vector_index()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
    lg_store.set_store_config(config_)
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
    _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
    _check_pkg(pkg)
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
    raise ImportError(
ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`

17/05/2025, 20:33:20 Application startup failed. Exiting.
17/05/2025, 20:33:54 2025-05-17 18:33:54 [info     ] Using langgraph_runtime_postgres
17/05/2025, 20:33:54 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:33:54 Health server started at http://0.0.0.0:8000
17/05/2025, 20:33:54 Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/api/langgraph_api/queue_entrypoint.py", line 75, in <module>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
17/05/2025, 20:33:54     return runner.run(main)
17/05/2025, 20:33:54            ^^^^^^^^^^^^^^^^
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
17/05/2025, 20:33:54     return self._loop.run_until_complete(task)
17/05/2025, 20:33:54            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:33:54   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
17/05/2025, 20:33:54   File "/api/langgraph_api/queue_entrypoint.py", line 57, in entrypoint
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
17/05/2025, 20:33:54     return await anext(self.gen)
17/05/2025, 20:33:54            ^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
17/05/2025, 20:33:54     await database.start_pool()
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
17/05/2025, 20:33:54     await migrate_vector_index()
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
17/05/2025, 20:33:54     lg_store.set_store_config(config_)
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
17/05/2025, 20:33:54     _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
17/05/2025, 20:33:54                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:33:54   File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
17/05/2025, 20:33:54     _check_pkg(pkg)
17/05/2025, 20:33:54   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
17/05/2025, 20:33:54     raise ImportError(
17/05/2025, 20:33:54 ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`
17/05/2025, 20:38:32 Using langgraph_runtime_postgres
17/05/2025, 20:38:32 Using auth of type=langsmith
17/05/2025, 20:38:32 Started server process [1]
17/05/2025, 20:38:32 Waiting for application startup.
17/05/2025, 20:38:32 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:38:32 Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 692, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
    await database.start_pool()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
    await migrate_vector_index()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
    lg_store.set_store_config(config_)
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
    _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
    _check_pkg(pkg)
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
    raise ImportError(
ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`

17/05/2025, 20:38:32 Application startup failed. Exiting.
17/05/2025, 20:39:04 2025-05-17 18:39:04 [info     ] Using langgraph_runtime_postgres
17/05/2025, 20:39:04 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:39:04 Health server started at http://0.0.0.0:8000
17/05/2025, 20:39:04 Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/api/langgraph_api/queue_entrypoint.py", line 75, in <module>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
17/05/2025, 20:39:04     return runner.run(main)
17/05/2025, 20:39:04            ^^^^^^^^^^^^^^^^
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
17/05/2025, 20:39:04     return self._loop.run_until_complete(task)
17/05/2025, 20:39:04            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:39:04   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
17/05/2025, 20:39:04   File "/api/langgraph_api/queue_entrypoint.py", line 57, in entrypoint
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
17/05/2025, 20:39:04     return await anext(self.gen)
17/05/2025, 20:39:04            ^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
17/05/2025, 20:39:04     await database.start_pool()
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
17/05/2025, 20:39:04     await migrate_vector_index()
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
17/05/2025, 20:39:04     lg_store.set_store_config(config_)
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
17/05/2025, 20:39:04     _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
17/05/2025, 20:39:04                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:39:04   File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
17/05/2025, 20:39:04     _check_pkg(pkg)
17/05/2025, 20:39:04   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
17/05/2025, 20:39:04     raise ImportError(
17/05/2025, 20:39:04 ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`
17/05/2025, 20:43:45 Using langgraph_runtime_postgres
17/05/2025, 20:43:45 Using auth of type=langsmith
17/05/2025, 20:43:45 Started server process [1]
17/05/2025, 20:43:45 Waiting for application startup.
17/05/2025, 20:43:45 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:43:45 Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 692, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
    await database.start_pool()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
    await migrate_vector_index()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
    lg_store.set_store_config(config_)
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
    _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
    _check_pkg(pkg)
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
    raise ImportError(
ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`

17/05/2025, 20:43:45 Application startup failed. Exiting.
17/05/2025, 20:44:09 2025-05-17 18:44:09 [info     ] Using langgraph_runtime_postgres
17/05/2025, 20:44:09 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:44:09 Health server started at http://0.0.0.0:8000
17/05/2025, 20:44:09 Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/api/langgraph_api/queue_entrypoint.py", line 75, in <module>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
17/05/2025, 20:44:09     return runner.run(main)
17/05/2025, 20:44:09            ^^^^^^^^^^^^^^^^
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
17/05/2025, 20:44:09     return self._loop.run_until_complete(task)
17/05/2025, 20:44:09            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:44:09   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
17/05/2025, 20:44:09   File "/api/langgraph_api/queue_entrypoint.py", line 57, in entrypoint
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
17/05/2025, 20:44:09     return await anext(self.gen)
17/05/2025, 20:44:09            ^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
17/05/2025, 20:44:09     await database.start_pool()
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
17/05/2025, 20:44:09     await migrate_vector_index()
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
17/05/2025, 20:44:09     lg_store.set_store_config(config_)
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
17/05/2025, 20:44:09     _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
17/05/2025, 20:44:09                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:44:09   File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
17/05/2025, 20:44:09     _check_pkg(pkg)
17/05/2025, 20:44:09   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
17/05/2025, 20:44:09     raise ImportError(
17/05/2025, 20:44:09 ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`
17/05/2025, 20:48:55 Using langgraph_runtime_postgres
17/05/2025, 20:48:55 Using auth of type=langsmith
17/05/2025, 20:48:55 Started server process [1]
17/05/2025, 20:48:55 Waiting for application startup.
17/05/2025, 20:48:55 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:48:55 Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 692, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
    await database.start_pool()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
    await migrate_vector_index()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
    lg_store.set_store_config(config_)
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
    _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
    _check_pkg(pkg)
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
    raise ImportError(
ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`

17/05/2025, 20:48:55 Application startup failed. Exiting.
17/05/2025, 20:49:18 2025-05-17 18:49:18 [info     ] Using langgraph_runtime_postgres
17/05/2025, 20:49:18 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:49:18 Health server started at http://0.0.0.0:8000
17/05/2025, 20:49:18 Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/api/langgraph_api/queue_entrypoint.py", line 75, in <module>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
17/05/2025, 20:49:18     return runner.run(main)
17/05/2025, 20:49:18            ^^^^^^^^^^^^^^^^
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
17/05/2025, 20:49:18     return self._loop.run_until_complete(task)
17/05/2025, 20:49:18            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:49:18   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
17/05/2025, 20:49:18   File "/api/langgraph_api/queue_entrypoint.py", line 57, in entrypoint
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
17/05/2025, 20:49:18     return await anext(self.gen)
17/05/2025, 20:49:18            ^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
17/05/2025, 20:49:18     await database.start_pool()
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
17/05/2025, 20:49:18     await migrate_vector_index()
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
17/05/2025, 20:49:18     lg_store.set_store_config(config_)
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
17/05/2025, 20:49:18     _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
17/05/2025, 20:49:18                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:49:18   File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
17/05/2025, 20:49:18     _check_pkg(pkg)
17/05/2025, 20:49:18   File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
17/05/2025, 20:49:18     raise ImportError(
17/05/2025, 20:49:18 ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`
17/05/2025, 20:53:58 Using langgraph_runtime_postgres
17/05/2025, 20:53:58 Using auth of type=langsmith
17/05/2025, 20:53:58 Started server process [1]
17/05/2025, 20:53:58 Waiting for application startup.
17/05/2025, 20:53:58 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:53:58 Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 692, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 51, in lifespan
    await database.start_pool()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 220, in start_pool
    await migrate_vector_index()
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/database.py", line 204, in migrate_vector_index
    lg_store.set_store_config(config_)
  File "/usr/local/lib/python3.11/site-packages/langgraph_runtime_postgres/store.py", line 49, in set_store_config
    _STORE_CONFIG["index"]["embed"] = resolve_embeddings(_STORE_CONFIG["index"])
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/api/langgraph_api/graph.py", line 598, in resolve_embeddings
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 181, in init_embeddings
    _check_pkg(pkg)
  File "/usr/local/lib/python3.11/site-packages/langchain/embeddings/base.py", line 112, in _check_pkg
    raise ImportError(
ImportError: Could not import langchain_openai python package. Please install it with `pip install langchain_openai`

17/05/2025, 20:53:58 Application startup failed. Exiting.
17/05/2025, 20:54:25 2025-05-17 18:54:25 [info     ] Using langgraph_runtime_postgres
17/05/2025, 20:54:25 Starting Postgres runtime with langgraph-api=0.2.27
17/05/2025, 20:54:25 Health server started at http://0.0.0.0:8000
17/05/2025, 20:54:25 Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/api/langgraph_api/queue_entrypoint.py", line 75, in <module>
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
17/05/2025, 20:54:25     return runner.run(main)
17/05/2025, 20:54:25            ^^^^^^^^^^^^^^^^
17/05/2025, 20:54:25   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
17/05/2025, 20:54:25     return self._loop.run_until_complete(task)
17/05/2025, 20:54:25            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
17/05/2025, 20:54:25   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
17/05/2025, 20:54:25   File "/api/langgraph_api/queue_entrypoint.py", line 57, in entrypoint
17/05/2025, 20:54:25   File "/usr/local/lib/python3.11/contextlib.py", line 210, in __aenter__
17/05/2025, 20:54:25     return await anext(self.gen)