USE carsales;

-- Tabela base (MotorVehicle)
CREATE TABLE motor_vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model VARCHAR(100),
    year VARCHAR(20),
    mileage INT,
    fuel_type VARCHAR(20),
    color VARCHAR(50),
    city VARCHAR(100),
    additional_description TEXT,
    price INT UNSIGNED,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para carros
CREATE TABLE cars (
    vehicle_id INT PRIMARY KEY,
    bodywork VARCHAR(20),
    transmission VARCHAR(20),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES motor_vehicles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para motos
CREATE TABLE motorcycles (
    vehicle_id INT PRIMARY KEY,
    starter VARCHAR(20),
    fuel_system VARCHAR(20),
    engine_displacement DECIMAL(8, 2) UNSIGNED,
    cooling VARCHAR(20),
    style VARCHAR(20),
    engine_type VARCHAR(30),
    gears SMALLINT UNSIGNED,
    front_rear_brake VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES motor_vehicles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para imagens
CREATE TABLE vehicle_images (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL,
  filename VARCHAR(255) NOT NULL,
  path VARCHAR(500) NOT NULL,
  thumbnail_path VARCHAR(500),
  position SMALLINT UNSIGNED,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (vehicle_id) REFERENCES motor_vehicles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para itens dos carros
CREATE TABLE car_items (
    car_id INT NOT NULL,
    item VARCHAR(100) NOT NULL,
    PRIMARY KEY (car_id, item),
    FOREIGN KEY (car_id) REFERENCES cars(vehicle_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
