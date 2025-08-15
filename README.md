# 🚗 Car Sales API - Sistema de Vendas de Veículos

## 📋 Sobre o Projeto

O **Car Sales API** é um sistema completo para gerenciamento de vendas de veículos (carros e motocicletas) desenvolvido em **Python** com **FastAPI**. O projeto implementa uma arquitetura hexagonal (ports and adapters) garantindo separação clara de responsabilidades e facilidade de manutenção.

### ✨ Principais Funcionalidades

- **🚗 Gestão de Veículos**: CRUD completo para carros e motocicletas
- **👥 Gestão de Clientes**: Cadastro e gerenciamento de clientes
- **👨‍💼 Gestão de Funcionários**: Controle de colaboradores
- **💰 Gestão de Vendas**: Registro e acompanhamento de vendas
- **💬 Sistema de Mensagens**: Comunicação com clientes e atribuição de responsáveis
- **📸 Upload de Imagens**: Sistema completo de imagens para veículos com thumbnails
- **🔍 Filtros Avançados**: Busca por preço, status, data, etc.
- **📊 Paginação**: Listagem otimizada com skip/limit

## 🏗️ Arquitetura e Tecnologias

### 📐 Arquitetura Hexagonal
```
├──  Domain (Domínio)
│   ├── entities/          # Entidades de negócio
│   ├── ports/            # Interfaces (contratos)
│   └── services/         # Serviços de domínio
├──  Application (Aplicação)
│   ├── dtos/             # Data Transfer Objects
│   └── services/         # Serviços de aplicação
└──  Infrastructure (Infraestrutura)
    ├── adapters/driving/  # Controllers/Routes (entrada)
    └── adapters/driven/   # Database/Persistence (saída)
```

### 🛠️ Stack Tecnológico

- **🐍 Python 3.13** - Linguagem principal
- **⚡ FastAPI** - Framework web moderno e rápido
- **🗄️ MySQL 8.0** - Banco de dados relacional
- **📊 SQLAlchemy** - ORM para Python
- **✅ Pydantic** - Validação de dados
- **🐳 Docker & Docker Compose** - Containerização
- **🖼️ Pillow (PIL)** - Processamento de imagens
- **📝 Swagger/OpenAPI** - Documentação automática da API

## 🚀 Como Usar Localmente

### 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Git** para clonar o repositório

### 🔧 Configuração

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/LeonardoComar/fase-1-car-sales.git
   cd fase-1-car-sales
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   # Renomeie o arquivo de exemplo para .env
   cp .env.example .env
   ```

3. **Inicie a aplicação:**
   ```bash
   docker compose up
   ```

   Ou para executar em background:
   ```bash
   docker compose up -d
   ```

### 🌐 Acessos

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🌐 **API Principal** | http://localhost:8180 | Endpoint base da API |
| 📖 **Documentação Swagger** | http://localhost:8180/docs | Interface interativa da API |
| 📋 **ReDoc** | http://localhost:8180/redoc | Documentação alternativa |

### � Autenticação Automática

A aplicação cria automaticamente um usuário administrador na primeira execução:

| Campo | Valor |
|-------|--------|
| 📧 **Email** | `admin@carsales.com` |
| 🔑 **Senha** | `admin123456` |
| 👑 **Perfil** | Administrador |

### �📮 Postman
1. Importe as collections da pasta `📁 Postman/`:
   - `Car Sales.postman_collection.json` - Todas as requisições
   - `Car Sales.postman_environment.json` - Variáveis de ambiente

#### 🔧 **Configuração Automática de Token no Postman:**
- ✅ **Script de Login Automático** - A rota de login captura automaticamente o token JWT
- ✅ **Variável de Ambiente** - Token é salvo como `{{access_token}}`
- ✅ **Headers Pré-configurados** - Todas as rotas protegidas já incluem `Authorization: Bearer {{access_token}}`
- ✅ **Renovação Automática** - Basta fazer login novamente para atualizar o token

## 📚 Documentação Adicional

### 📖 Documentação Completa
- **📄 PDF:** `Documentação/Documentação.pdf`
- **📝 Word:** `Documentação/Documentação.docx`
- **🎯 Domain Storytelling:** `Documentação/Domain Storytelling/`
