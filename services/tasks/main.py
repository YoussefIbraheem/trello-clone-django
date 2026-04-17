from app import settings, create_app
from utils.openapi.path_converter import FlaskPathConverter
from utils.openapi.route_collector import RouteCollector
from utils.openapi.schema_collector import SchemaCollector
from utils.openapi.doc_generator import OpenAPIDocGenerator
from app.db.database import get_db_session, create_tables
from swagger_ui import api_doc
app = create_app()

def initiate_swagger_ui():
    converter = FlaskPathConverter()
    routes_c = RouteCollector(app,converter)
    schemas_c = SchemaCollector("app.schemas")
    generator = OpenAPIDocGenerator(routes_c,schemas_c)
    output_path = "./openapi.yaml"

    try:
        generator.generate(output_path)
        api_doc(app,config_path=output_path,url_prefix="/api/swagger",title="API Doc")
    except Exception as e:
        print(f"OpenAPI generation Error:{e}")


@app.route(f"{settings.API_V1_PREFIX}")
def index():
    return f"Welcome to the {settings.SERVICE_NAME} service (version {settings.SERVICE_VERSION})!"



if __name__ == "__main__":
    
    initiate_swagger_ui()
    create_tables()
    
    print(
        f"Starting {settings.SERVICE_NAME} service (version {settings.SERVICE_VERSION}) on {settings.HOST}:{settings.PORT} with debug={settings.DEBUG}"
    )

    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
