# CDH-BE

2024년 종합전공PBL "J3PBL" 팀의 백엔드 레포지토리입니다.

## 프로젝트 개요

<img width="799" height="257" alt="백엔드시스템" src="https://github.com/user-attachments/assets/f47a325b-a62c-4ffa-827a-99068dbc6eb7" />

**STACK**은 개발자들의 협업 프로젝트를 종합적으로 관리하고 더 나은 프로젝트를 제작할 수 있도록 돕는 AI 기반 프로젝트 관리 시스템입니다.
이 프로젝트는 다음과 같은 기능을 제공합니다.

-   **프로젝트 관리**: 사용자가 노트, ERD, API 명세서를 개인 또는 팀스페이스 단위로 관리할 수 있도록 지원합니다.
-   **프로젝트 분석**: 사용자의 프로젝트를 CRAG(Corrective Retrieval Augmented Generation) 및 프롬프트 엔지니어링 기술을 통해 할루시네이션을 방지하며 프로젝트를 정밀 분석합니다.

## 기술 스택

### 주요 기술

-   **언어**: Python 3.11
-   **프레임워크**: FastAPI
-   **AI/ML**:
    -   LangChain, LangGraph, Langserve: AI 에이전트 및 그래프 기반 워크플로우 관리
    -   Langchain-OpenAI: OpenAI 모델 연동
    -   langchain_community.vectorstores, langchain_openai.embeddings, Faiss-cpu: 벡터 임베딩 및 벡터 스토어 및 검색
    -   DuckDuckGo-Search: 웹 검색
-   **데이터베이스**: MySQL (Docker Image: mysql:8.0), SQLAlchemy (비동기 통신), Alembic
-   **컨테이너**: Docker, Docker Compose
-   **데브옵스 (CI/CD)**: GitHub Action, Docker Hub
-   **배포**: Nginx (리버스 프록시 및 SSL/TLS) , AWS EC2 , AWS RDS

### 아키텍처

``docker-compose.yaml`` 파일은 로컬 개발 환경을 기준으로 구성되어 있습니다.

-   **FastAPI Backend (local)**: API 엔드포인트를 처리하는 메인 애플리케이션 서버입니다.
-   **MySQL (db)**: 프로젝트 데이터를 저장하는 관계형 데이터베이스 서버입니다.

## 설치 및 실행 방법

### 사전 요구 사항

-   Docker
-   Docker Compose

### 실행 절차

1.  **레포지토리 클론**:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/CDH-BE-1.git]
    cd CDH-BE-1
    ```

2.  **환경 변수 설정**:
    `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.
    ```bash
    # DB 설정
    DB_user=root
    DB_host=db
    DB_port=3306
    DB_password=
    DB_path=./faiss_db
    TEST_DB_path=../../faiss_db

    # 도커 설정
    DOCKER_USERNAME=your_docker_username
    DOCKER_FILENAME=your_docker_file
    version=local

    # 인증 설정
    ACCESS_TOKEN_EXPIRE_MINUTES=1440
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256

    # Langchain 설정
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
    LANGCHAIN_API_KEY=your_langsmith_api_key
    LANGCHAIN_PROJECT=your_langsmith_project_name

    # API 설정
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_REDIRECT_URI=your_server_redirect_url
    ```

3.  **Docker Compose를 이용한 실행**:
    - **개발 환경**
        ```bash
        docker-compose -f docker-compose.yaml up --build
        ```
    - **배포 환경 (Nginx 포함)**
        ```bash
        # 1. 네트워크 생성
        docker network create app_network

        # 2. FastAPI 실행
        docker-compose -f docker-compose.yaml up --build -d
        ```

   
