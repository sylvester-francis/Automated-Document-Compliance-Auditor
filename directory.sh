mkdir -p ./app/{models,services,static/{css,js,img},templates/{documents,compliance},utils,routes}
mkdir -p ./instance
touch ./app/__init__.py
touch ./app/config.py
touch ./app/models/__init__.py
touch ./app/models/{document.py,compliance.py}
touch ./app/services/__init__.py
touch ./app/services/{document_service.py,extraction_service.py,rule_engine.py,llm_service.py}
touch ./app/utils/__init__.py
touch ./app/utils/{pdf_utils.py,text_processing.py}
touch ./app/routes/__init__.py
touch ./app/routes/{main.py,documents.py,compliance.py}
touch ./app/templates/base.html
touch ./app/templates/index.html
touch ./.gitignore
touch ./README.md