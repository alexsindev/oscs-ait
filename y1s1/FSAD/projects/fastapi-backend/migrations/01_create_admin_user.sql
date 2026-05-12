-- Create admin user if not exists
-- Password: admin123 (bcrypt hash)

DO $$
DECLARE
    admin_email VARCHAR := 'admin@test.com';
    admin_exists BOOLEAN;
BEGIN
    -- Check if admin user already exists
    SELECT EXISTS(SELECT 1 FROM users WHERE email = admin_email) INTO admin_exists;
    
    IF NOT admin_exists THEN
        -- Insert admin user with bcrypt hashed password for 'admin123'
        -- Hash generated with: python -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())"
        INSERT INTO users (
            id,
            first_name,
            last_name,
            email,
            hashed_password,
            role,
            is_approved
        ) VALUES (
            gen_random_uuid(),
            'Admin',
            'User',
            admin_email,
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYZ5qU5Rm4K',  -- admin123
            'admin',
            true
        );
        
        RAISE NOTICE 'Admin user created successfully: %', admin_email;
    ELSE
        RAISE NOTICE 'Admin user already exists: %', admin_email;
    END IF;
END $$;
