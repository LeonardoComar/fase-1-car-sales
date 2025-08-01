CREATE USER 'carsales_user'@'%' IDENTIFIED BY 'Mudar123!';
GRANT ALL PRIVILEGES ON carsales.* TO 'carsales_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;