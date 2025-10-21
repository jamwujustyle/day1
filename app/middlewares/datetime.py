from starlette.responses import JSONResponse
import json
from datetime import datetime


def register_datetime_middleware(app):
    @app.middleware("http")
    async def datetime_converter_middleware(request, call_next):
        response = await call_next(request)

        # only handle JSON responses
        if response.headers.get("content-type", "").startswith("application/json"):
            # read the full response body
            body = b"".join([chunk async for chunk in response.body_iterator])
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return response

            def convert_dt(obj):
                if isinstance(obj, dict):
                    return {k: convert_dt(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_dt(i) for i in obj]
                elif isinstance(obj, str):
                    try:
                        dt = datetime.fromisoformat(obj.replace("Z", "+00:00"))
                        return dt.strftime("%Y-%m-%d %H:%M")
                    except ValueError:
                        return obj
                return obj

            converted = convert_dt(data)

            new_response = JSONResponse(
                content=converted, status_code=response.status_code
            )
            # ✅ copy cookies
            for cookie in response.raw_headers:
                if cookie[0].decode("utf-8").lower() == "set-cookie":
                    new_response.raw_headers.append(cookie)
            # ✅ copy other headers
            for key, value in response.headers.items():
                if key.lower() != "content-length":
                    new_response.headers[key] = value

            return new_response

        return response
