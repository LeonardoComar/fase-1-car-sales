-- Usar o banco de dados
USE carsales;

-- Criar usuário se não existir
CREATE USER IF NOT EXISTS 'carsales_user'@'%' IDENTIFIED BY 'Mudar123!';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON carsales.* TO 'carsales_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;