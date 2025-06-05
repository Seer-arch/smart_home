-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建房屋表
CREATE TABLE IF NOT EXISTS houses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    area DECIMAL(10,2) NOT NULL,
    description TEXT,
    house_metadata TEXT,
    floor_count INTEGER,
    room_count INTEGER,
    building_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建房间表
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    house_id INTEGER REFERENCES houses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    area DECIMAL(10,2) NOT NULL,
    room_type VARCHAR(50) NOT NULL,
    description TEXT,
    room_metadata JSON,
    floor INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建设备表
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    installation_date DATE,
    last_maintenance TIMESTAMP,
    next_maintenance TIMESTAMP,
    description TEXT,
    device_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建设备使用记录表
CREATE TABLE IF NOT EXISTS device_usage_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration FLOAT,
    energy_consumption DECIMAL(10,2),
    status VARCHAR(50) NOT NULL,
    usage_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建设备维护记录表
CREATE TABLE IF NOT EXISTS device_maintenance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    maintenance_date TIMESTAMP NOT NULL,
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT,
    cost DECIMAL(10,2),
    maintenance_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建安防事件表
CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    house_id INTEGER NOT NULL,
    device_id INTEGER REFERENCES devices(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    event_time TIMESTAMP NOT NULL,
    description TEXT,
    severity TEXT,
    status TEXT,
    event_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (house_id) REFERENCES houses(id) ON DELETE CASCADE
);

-- 创建用户反馈表
CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_houses_user_id ON houses(user_id);
CREATE INDEX IF NOT EXISTS idx_rooms_house_id ON rooms(house_id);
CREATE INDEX IF NOT EXISTS idx_devices_room_id ON devices(room_id);
CREATE INDEX IF NOT EXISTS idx_device_usage_records_device_id ON device_usage_records(device_id);
CREATE INDEX IF NOT EXISTS idx_device_maintenance_records_device_id ON device_maintenance_records(device_id);
CREATE INDEX IF NOT EXISTS idx_security_events_house_id ON security_events(house_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_device_id ON user_feedback(device_id);

-- 插入测试数据
INSERT INTO users (email, hashed_password, full_name, phone_number) VALUES
('test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpR1IOBYyGqK8y', '测试用户1', '13800138001'),
('test2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpR1IOBYyGqK8y', '测试用户2', '13800138002');

-- 插入测试房屋
INSERT INTO houses (user_id, name, address, area, description, house_metadata, floor_count, room_count, building_type) VALUES
(1, '测试房屋1', '北京市海淀区测试路1号', 120.50, '现代风格别墅', '{"style": "现代", "year_built": 2020}', 3, 4, '别墅'),
(2, '测试房屋2', '北京市朝阳区测试路2号', 150.75, '简约风格公寓', '{"style": "简约", "year_built": 2021}', 2, 3, '公寓');

-- 插入测试房间
INSERT INTO rooms (house_id, name, area, room_type, floor) VALUES
(1, '客厅', 30.50, 'living_room', 1),
(1, '主卧', 20.25, 'bedroom', 2),
(1, '厨房', 15.75, 'kitchen', 1),
(2, '客厅', 35.00, 'living_room', 1),
(2, '主卧', 25.00, 'bedroom', 2),
(2, '厨房', 18.00, 'kitchen', 1);

-- 插入测试设备
INSERT INTO devices (room_id, name, device_type, status, manufacturer, model, installation_date) VALUES
(1, '智能空调', 'air_conditioner', 'active', '格力', 'KFR-35GW', '2024-01-01'),
(1, '智能电视', 'tv', 'active', '小米', 'L55M5', '2024-01-01'),
(2, '智能灯', 'light', 'active', '飞利浦', 'Hue', '2024-01-01'),
(3, '智能冰箱', 'refrigerator', 'active', '海尔', 'BCD-452WDPF', '2024-01-01'),
(4, '智能空调', 'air_conditioner', 'active', '美的', 'KFR-35GW', '2024-01-01'),
(5, '智能灯', 'light', 'active', '欧普', 'OPPLE', '2024-01-01'),
(6, '智能烤箱', 'oven', 'active', '西门子', 'HB514GEW0W', '2024-01-01');

-- 插入测试使用记录
INSERT INTO device_usage_records (device_id, user_id, start_time, end_time, duration, energy_consumption, status, usage_metadata) VALUES
(1, 1, '2024-01-01 08:00:00', '2024-01-01 12:00:00', 240.0, 2.5, 'completed', '{"temperature": 25, "humidity": 50}'),
(1, 1, '2024-01-01 14:00:00', '2024-01-01 18:00:00', 240.0, 2.5, 'completed', '{"temperature": 26, "humidity": 55}'),
(2, 1, '2024-01-01 19:00:00', '2024-01-01 22:00:00', 180.0, 1.5, 'completed', '{"temperature": 24, "humidity": 45}'),
(3, 2, '2024-01-01 18:00:00', '2024-01-01 23:00:00', 300.0, 0.5, 'completed', '{"temperature": 23, "humidity": 40}');

-- 插入测试维护记录
INSERT INTO device_maintenance_records (device_id, maintenance_date, maintenance_type, description, cost, maintenance_metadata) VALUES
(1, '2024-01-15 10:00:00', 'regular', '定期清洗滤网', 100.00, '{"filter_cleaned": true}'),
(2, '2024-01-20 14:00:00', 'repair', '更换电源板', 500.00, '{"new_power_board": true}'),
(3, '2024-01-25 09:00:00', 'regular', '更换灯泡', 50.00, '{"new_light_bulb": true}');

-- 插入测试安防事件
INSERT INTO security_events (house_id, device_id, event_type, event_time, description, severity, status, event_metadata) VALUES
(1, 1, 'motion_detected', '2024-03-20 10:00:00', '检测到客厅有异常活动', 'high', 'pending', '{"location": "客厅", "confidence": 0.95}'),
(1, 2, 'door_opened', '2024-03-20 10:05:00', '前门被打开', 'medium', 'resolved', '{"door_id": "front_door", "user_id": 1}'),
(2, 3, 'smoke_detected', '2024-03-20 11:00:00', '厨房检测到烟雾', 'high', 'investigating', '{"sensor_id": "kitchen_smoke_1", "smoke_level": 0.8}');

-- 插入测试用户反馈
INSERT INTO user_feedback (user_id, device_id, rating, comment) VALUES
(1, 1, 5, '空调制冷效果很好'),
(1, 2, 4, '电视画质清晰，但遥控器反应有点慢'),
(2, 4, 5, '空调静音效果很好'),
(2, 5, 4, '灯光调节很方便'); 