# from fastapi.security import APIKeyCookie

# cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


# def get_swagger_ui_html(openapi_url: str, title: str):
#     return f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>{title}</title>
#         <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3/swagger-ui.css">
#     </head>
#     <body>
#         <div id="swagger-ui"></div>
#         <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
#         <script>
#         const ui = SwaggerUIBundle({{
#             url: "{openapi_url}",
#             dom_id: '#swagger-ui',
#             presets: [
#             SwaggerUIBundle.presets.apis,
#             SwaggerUIBundle.SwaggerUIStandalonePreset
#             ],
#             layout: "BaseLayout",
#             deepLinking: true,
#             showExtensions: true,
#             showCommonExtensions: true,
#             operationsSorter: "alpha",
#             onComplete: function() {{
#                 ui.preauthorizeApiKey("cookieAuth", "YOUR_ACCESS_TOKEN");
#             }}
#         }})
#         </script>
#     </body>
#     </html>
#     """
