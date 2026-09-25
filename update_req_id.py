import sys
import re

with open('apps/api/src/apps/api/app/middleware/request_id.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''        request_id = incoming if incoming and _VALID_REQUEST_ID.fullmatch(incoming) else uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id

        # Set telemetry context
        from shared.logging.context import set_telemetry_context, reset_telemetry_context
        token = set_telemetry_context({"request_id": request_id})
        
        try:
            async def add_request_id(message: Message) -> None:
                if message["type"] == "http.response.start":
                    headers = MutableHeaders(scope=message)
                    headers[self._header_name] = request_id
                await send(message)

            await self._application(scope, receive, add_request_id)
        finally:
            reset_telemetry_context(token)'''

content = re.sub(r'        request_id = incoming.*        await self._application\(scope, receive, add_request_id\)', replacement, content, flags=re.DOTALL)

with open('apps/api/src/apps/api/app/middleware/request_id.py', 'w', encoding='utf-8') as f:
    f.write(content)
