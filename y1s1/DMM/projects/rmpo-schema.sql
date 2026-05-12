CREATE DATABASE rmpo;

CREATE TABLE IF NOT EXISTS rmpo.projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    keywords VARCHAR(500),
    category VARCHAR(100),
    research_area VARCHAR(150),
    duration_months INT,
    contract_start_date DATE,
    contract_end_date DATE,
    total_budget DECIMAL(15,2),
    project_status ENUM('Planning', 'Active', 'Completed', 'Cancelled', 'On Hold') DEFAULT 'Planning',
    creation_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    
    INDEX idx_project_status (project_status),
    INDEX idx_project_category (category),
    INDEX idx_project_research_area (research_area),
    INDEX idx_project_dates (contract_start_date, contract_end_date)
);

CREATE TABLE IF NOT EXISTS rmpo.departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(150) NOT NULL,
    department_code VARCHAR(20) UNIQUE NOT NULL,
    head_of_department VARCHAR(100),
    contact_info VARCHAR(255),
    building_location VARCHAR(100),
    
    INDEX idx_dept_code (department_code),
    INDEX idx_dept_name (department_name)
);

CREATE TABLE IF NOT EXISTS rmpo.people (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    person_type ENUM('Faculty', 'Staff', 'Student', 'Researcher', 'PostDoc', 'Contractor') NOT NULL,
    expertise_area VARCHAR(200),
    hire_date DATE,
    position_title VARCHAR(150),
    role VARCHAR(100),
    department_id INT,
    
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    
    INDEX idx_person_email (email),
    INDEX idx_person_type (person_type),
    INDEX idx_person_name (last_name, first_name),
    INDEX idx_person_dept (department_id)
);

CREATE TABLE IF NOT EXISTS rmpo.donor_sponsors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    donor_type ENUM('Government', 'Private Foundation', 'Corporate', 'Individual', 'NGO', 'International') NOT NULL,
    contact_person VARCHAR(150),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    country VARCHAR(100),
    
    INDEX idx_donor_org (organization_name),
    INDEX idx_donor_type (donor_type),
    INDEX idx_donor_country (country)
);

-- Create relationship/junction tables

CREATE TABLE IF NOT EXISTS rmpo.budget_installments (
    installment_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    installment_number INT NOT NULL,
    installment_date DATE,
    budget_percentage DECIMAL(5,2) CHECK (budget_percentage >= 0 AND budget_percentage <= 100),
    amount DECIMAL(15,2) NOT NULL,
    payment_status ENUM('Pending', 'Paid', 'Overdue', 'Cancelled') DEFAULT 'Pending',
    due_date DATE,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_project_installment (project_id, installment_number),
    INDEX idx_installment_status (payment_status),
    INDEX idx_installment_due (due_date)
);

CREATE TABLE IF NOT EXISTS rmpo.project_personnels (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    person_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active ENUM('Yes', 'No') DEFAULT 'Yes',
    specific_responsibilities TEXT,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(person_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_active_assignment (project_id, person_id, is_active),
    INDEX idx_personnel_project (project_id),
    INDEX idx_personnel_person (person_id),
    INDEX idx_personnel_active (is_active),
    INDEX idx_personnel_dates (start_date, end_date)
);

CREATE TABLE IF NOT EXISTS rmpo.project_fundings (
    funding_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    donor_id INT NOT NULL,
    funding_amount DECIMAL(15,2) NOT NULL,
    funding_percentage DECIMAL(5,2) CHECK (funding_percentage >= 0 AND funding_percentage <= 100),
    funding_start_date DATE,
    funding_end_date DATE,
    funding_status ENUM('Pending', 'Active', 'Completed', 'Cancelled') DEFAULT 'Pending',
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES donor_sponsors(donor_id) ON DELETE CASCADE,
    
    INDEX idx_funding_project (project_id),
    INDEX idx_funding_donor (donor_id),
    INDEX idx_funding_status (funding_status),
    INDEX idx_funding_dates (funding_start_date, funding_end_date)
);

CREATE TABLE IF NOT EXISTS rmpo.project_departments (
    involvement_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    department_id INT NOT NULL,
    involvement_type ENUM('Lead', 'Collaborator', 'Support', 'Advisory') NOT NULL,
    involvement_start DATE,
    involvement_end DATE,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_project_dept_involvement (project_id, department_id, involvement_type),
    INDEX idx_proj_dept_project (project_id),
    INDEX idx_proj_dept_department (department_id),
    INDEX idx_proj_dept_type (involvement_type)
);

CREATE TABLE IF NOT EXISTS rmpo.student_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    project_id INT NOT NULL,
    responsibility VARCHAR(255),
    max_hours_per_month INT CHECK (max_hours_per_month > 0),
    rate_per_hour DECIMAL(8,2) CHECK (rate_per_hour >= 0),
    start_date DATE NOT NULL,
    end_date DATE,
    assignment_status ENUM('Active', 'Completed', 'Terminated', 'Suspended') DEFAULT 'Active',
    
    FOREIGN KEY (person_id) REFERENCES people(person_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    
    INDEX idx_student_person (person_id),
    INDEX idx_student_project (project_id),
    INDEX idx_student_status (assignment_status),
    INDEX idx_student_dates (start_date, end_date)
);

CREATE TABLE IF NOT EXISTS rmpo.research_outputs (
    output_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    output_type ENUM('Publication', 'Patent', 'Report', 'Presentation', 'Dataset', 'Software', 'Prototype') NOT NULL,
    output_title VARCHAR(500) NOT NULL,
    publication_date DATE,
    venue VARCHAR(255),
    description TEXT,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    
    INDEX idx_output_project (project_id),
    INDEX idx_output_type (output_type),
    INDEX idx_output_date (publication_date),
    INDEX idx_output_title (output_title)
);

CREATE TABLE IF NOT EXISTS rmpo.milestones (
    milestone_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    milestone_name VARCHAR(255) NOT NULL,
    milestone_description TEXT,
    planned_date DATE,
    actual_date DATE,
    milestone_status ENUM('Pending', 'In Progress', 'Completed', 'Delayed', 'Cancelled') DEFAULT 'Pending',
    completion_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    
    INDEX idx_milestone_project (project_id),
    INDEX idx_milestone_status (milestone_status),
    INDEX idx_milestone_planned_date (planned_date),
    INDEX idx_milestone_actual_date (actual_date)
);

-- Insert sample data for testing with dynamic foreign key references

-- Insert departments
INSERT INTO rmpo.departments (department_name, department_code, head_of_department, contact_info, building_location) VALUES
('Computer Science', 'CS', 'Dr. John Smith', 'cs@university.edu', 'Science Building A'),
('Biology', 'BIO', 'Dr. Jane Doe', 'bio@university.edu', 'Life Sciences Center'),
('Engineering', 'ENG', 'Dr. Mike Johnson', 'eng@university.edu', 'Engineering Complex'),
('Physics', 'PHY', 'Dr. Sarah Wilson', 'physics@university.edu', 'Physics Research Center'),
('Mathematics', 'MATH', 'Dr. David Brown', 'math@university.edu', 'Mathematics Building'),
('Chemistry', 'CHEM', 'Dr. Lisa Garcia', 'chem@university.edu', 'Chemistry Laboratory Complex');

-- people roster
INSERT INTO rmpo.people (first_name, last_name, email, phone, person_type, expertise_area, hire_date, position_title, role, department_id) VALUES
('Alice', 'Johnson', 'alice.johnson@university.edu', '555-0101', 'Faculty', 'Machine Learning', '2020-01-15', 'Associate Professor', 'Principal Investigator', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'CS')),
('Bob', 'Chen', 'bob.chen@university.edu', '555-0102', 'Faculty', 'Bioinformatics', '2019-08-20', 'Assistant Professor', 'Co-Investigator', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'BIO')),
('Carol', 'Williams', 'carol.williams@university.edu', '555-0103', 'Student', 'Data Science', '2023-09-01', 'PhD Student', 'Research Assistant', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'CS')),
('Dr. Emily', 'Rodriguez', 'emily.rodriguez@university.edu', '555-0104', 'Faculty', 'Quantum Computing', '2018-03-10', 'Professor', 'Principal Investigator', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'PHY')),
('Dr. James', 'Park', 'james.park@university.edu', '555-0105', 'Faculty', 'Materials Science', '2021-07-01', 'Assistant Professor', 'Co-Investigator', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'ENG')),
('Dr. Maria', 'Santos', 'maria.santos@university.edu', '555-0106', 'Faculty', 'Environmental Chemistry', '2017-09-15', 'Associate Professor', 'Principal Investigator', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'CHEM')),
('Dr. Robert', 'Kim', 'robert.kim@university.edu', '555-0107', 'Faculty', 'Applied Mathematics', '2019-01-20', 'Professor', 'Co-Investigator', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'MATH')),
('Jennifer', 'Lee', 'jennifer.lee@university.edu', '555-0108', 'Student', 'Quantum Physics', '2022-08-25', 'PhD Student', 'Research Assistant', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'PHY')),
('Michael', 'Davis', 'michael.davis@university.edu', '555-0109', 'Student', 'Environmental Engineering', '2023-01-10', 'MS Student', 'Research Assistant', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'ENG')),
('Dr. Angela', 'Thompson', 'angela.thompson@university.edu', '555-0110', 'Faculty', 'Computational Chemistry', '2020-06-01', 'Assistant Professor', 'Co-Investigator', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'CHEM')),
('Thomas', 'Wang', 'thomas.wang@university.edu', '555-0111', 'Student', 'Biomedical Engineering', '2023-08-30', 'PhD Student', 'Research Assistant', 
    (SELECT department_id FROM rmpo.departments WHERE department_code = 'ENG'));

-- Donor/sponsor organizations
INSERT INTO rmpo.donor_sponsors (organization_name, donor_type, contact_person, contact_email, contact_phone, address, country) VALUES
('National Science Foundation', 'Government', 'Program Officer Smith', 'po.smith@nsf.gov', '703-555-0001', '2415 Eisenhower Avenue, Alexandria, VA 22314', 'USA'),
('Tech Innovation Foundation', 'Private Foundation', 'Sarah Lee', 'sarah.lee@techfound.org', '650-555-0002', '123 Innovation Drive, Palo Alto, CA 94301', 'USA'),
('Department of Energy', 'Government', 'Dr. Mark Stevens', 'mark.stevens@energy.gov', '202-555-0003', '1000 Independence Ave SW, Washington, DC 20585', 'USA'),
('Green Earth Foundation', 'Private Foundation', 'Elena Martinez', 'elena@greenearthfound.org', '415-555-0004', '456 Sustainability Blvd, San Francisco, CA 94102', 'USA'),
('Quantum Research Consortium', 'Corporate', 'Dr. Richard Taylor', 'rtaylor@quantumrc.org', '617-555-0005', '789 Innovation Square, Cambridge, MA 02139', 'USA'),
('Global Health Initiative', 'International', 'Dr. Priya Patel', 'priya.patel@globalhealth.org', '212-555-0006', '350 Fifth Avenue, New York, NY 10118', 'USA');

-- projects (8 total projects)
INSERT INTO rmpo.projects (title, description, keywords, category, research_area, duration_months, contract_start_date, contract_end_date, total_budget, project_status) VALUES
('AI-Driven Genomic Analysis', 'Development of machine learning algorithms for genomic sequence analysis', 'AI, genomics, machine learning, bioinformatics', 'Research', 'Computational Biology', 36, '2024-01-01', '2026-12-31', 750000.00, 'Active'),
('Smart Campus Infrastructure', 'IoT-based campus monitoring and optimization system', 'IoT, smart systems, sustainability', 'Applied Research', 'Computer Science', 24, '2024-06-01', '2026-05-31', 450000.00, 'Active'),
('Quantum Error Correction Algorithms', 'Development of novel quantum error correction methods for fault-tolerant quantum computing', 'quantum computing, error correction, algorithms, fault tolerance', 'Research', 'Quantum Physics', 48, '2023-09-01', '2027-08-31', 1200000.00, 'Active'),
('Sustainable Water Filtration Systems', 'Design and testing of eco-friendly water purification technologies using advanced materials', 'water filtration, sustainability, materials science, environmental', 'Applied Research', 'Environmental Engineering', 30, '2024-03-15', '2026-09-14', 580000.00, 'Active'),
('Mathematical Modeling of Climate Systems', 'Advanced mathematical models for predicting climate change impacts on regional ecosystems', 'climate modeling, mathematics, environmental science, predictive analytics', 'Research', 'Applied Mathematics', 42, '2023-11-01', '2027-04-30', 920000.00, 'Active'),
('Green Chemistry for Drug Discovery', 'Development of environmentally sustainable chemical processes for pharmaceutical research', 'green chemistry, pharmaceuticals, drug discovery, sustainable processes', 'Research', 'Chemistry', 36, '2024-02-01', '2027-01-31', 680000.00, 'Active'),
('Neural Network Hardware Acceleration', 'Design of specialized hardware architectures for efficient neural network computation', 'neural networks, hardware design, acceleration, computer architecture', 'Applied Research', 'Computer Engineering', 30, '2024-04-01', '2026-09-30', 520000.00, 'Active'),
('Biomedical Sensor Networks', 'Development of wireless sensor networks for real-time health monitoring applications', 'biomedical sensors, wireless networks, health monitoring, IoT', 'Applied Research', 'Biomedical Engineering', 24, '2024-07-01', '2026-06-30', 390000.00, 'Active');

-- Project funding relationships (using dynamic lookups)
INSERT INTO rmpo.project_fundings (project_id, donor_id, funding_amount, funding_percentage, funding_start_date, funding_end_date, funding_status) VALUES
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'National Science Foundation'), 
 500000.00, 66.67, '2024-01-01', '2026-12-31', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Tech Innovation Foundation'), 
 250000.00, 33.33, '2024-01-01', '2026-12-31', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'National Science Foundation'), 
 450000.00, 100.00, '2024-06-01', '2026-05-31', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Quantum Research Consortium'), 
 800000.00, 66.67, '2023-09-01', '2027-08-31', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Department of Energy'), 
 400000.00, 33.33, '2023-09-01', '2027-08-31', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Green Earth Foundation'), 
 350000.00, 60.34, '2024-03-15', '2026-09-14', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'National Science Foundation'), 
 230000.00, 39.66, '2024-03-15', '2026-09-14', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'National Science Foundation'), 
 550000.00, 59.78, '2023-11-01', '2027-04-30', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Department of Energy'), 
 370000.00, 40.22, '2023-11-01', '2027-04-30', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Global Health Initiative'), 
 480000.00, 70.59, '2024-02-01', '2027-01-31', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Tech Innovation Foundation'), 
 200000.00, 29.41, '2024-02-01', '2027-01-31', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Tech Innovation Foundation'), 
 320000.00, 61.54, '2024-04-01', '2026-09-30', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'National Science Foundation'), 
 200000.00, 38.46, '2024-04-01', '2026-09-30', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'Global Health Initiative'), 
 240000.00, 61.54, '2024-07-01', '2026-06-30', 'Active'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 
 (SELECT donor_id FROM rmpo.donor_sponsors WHERE organization_name = 'National Science Foundation'), 
 150000.00, 38.46, '2024-07-01', '2026-06-30', 'Active');

-- Project personnel assignments (using dynamic lookups)
INSERT INTO rmpo.project_personnels (project_id, person_id, start_date, end_date, is_active, specific_responsibilities) VALUES
-- Project 1: AI-Driven Genomic Analysis
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'alice.johnson@university.edu'), 
 '2024-01-01', NULL, 'Yes', 'Principal Investigator - Overall project leadership and AI algorithm development'),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'bob.chen@university.edu'), 
 '2024-01-01', NULL, 'Yes', 'Co-Investigator - Genomic data analysis and biological validation'),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'carol.williams@university.edu'), 
 '2024-02-01', NULL, 'Yes', 'Research Assistant - Data preprocessing and model training'),
-- Project 2: Smart Campus Infrastructure
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'alice.johnson@university.edu'), 
 '2024-06-01', NULL, 'Yes', 'Principal Investigator - System architecture and AI components'),
-- Project 3: Quantum Error Correction
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'emily.rodriguez@university.edu'), 
 '2023-09-01', NULL, 'Yes', 'Principal Investigator - Quantum algorithm design and theoretical analysis'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'robert.kim@university.edu'), 
 '2023-09-01', NULL, 'Yes', 'Co-Investigator - Mathematical foundations and optimization'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'jennifer.lee@university.edu'), 
 '2023-10-01', NULL, 'Yes', 'Research Assistant - Algorithm implementation and testing'),
-- Project 4: Sustainable Water Filtration
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'james.park@university.edu'), 
 '2024-03-15', NULL, 'Yes', 'Principal Investigator - Materials design and system engineering'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'maria.santos@university.edu'), 
 '2024-03-15', NULL, 'Yes', 'Co-Investigator - Environmental impact assessment and chemistry'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'michael.davis@university.edu'), 
 '2024-04-01', NULL, 'Yes', 'Research Assistant - Experimental testing and data analysis'),
-- Project 5: Climate Modeling
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'robert.kim@university.edu'), 
 '2023-11-01', NULL, 'Yes', 'Principal Investigator - Mathematical model development'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'maria.santos@university.edu'), 
 '2023-11-01', NULL, 'Yes', 'Co-Investigator - Environmental chemistry and validation'),
-- Project 6: Green Chemistry
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'maria.santos@university.edu'), 
 '2024-02-01', NULL, 'Yes', 'Principal Investigator - Green chemistry process development'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'angela.thompson@university.edu'), 
 '2024-02-01', NULL, 'Yes', 'Co-Investigator - Computational chemistry and molecular modeling'),
-- Project 7: Neural Network Hardware
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'alice.johnson@university.edu'), 
 '2024-04-01', NULL, 'Yes', 'Principal Investigator - Neural network optimization'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'james.park@university.edu'), 
 '2024-04-01', NULL, 'Yes', 'Co-Investigator - Hardware architecture design'),
-- Project 8: Biomedical Sensors
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'james.park@university.edu'), 
 '2024-07-01', NULL, 'Yes', 'Principal Investigator - Sensor network architecture'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 
 (SELECT person_id FROM rmpo.people WHERE email = 'thomas.wang@university.edu'), 
 '2024-07-15', NULL, 'Yes', 'Research Assistant - Biomedical applications and testing');

-- Department involvement in projects (using dynamic lookups)
INSERT INTO rmpo.project_departments (project_id, department_id, involvement_type, involvement_start, involvement_end) VALUES
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'CS'), 
 'Lead', '2024-01-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'BIO'), 
 'Collaborator', '2024-01-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'CS'), 
 'Lead', '2024-06-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'ENG'), 
 'Collaborator', '2024-06-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'PHY'), 
 'Lead', '2023-09-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'MATH'), 
 'Collaborator', '2023-09-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'ENG'), 
 'Lead', '2024-03-15', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'CHEM'), 
 'Collaborator', '2024-03-15', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'MATH'), 
 'Lead', '2023-11-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'CHEM'), 
 'Collaborator', '2023-11-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'CHEM'), 
 'Lead', '2024-02-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'CS'), 
 'Lead', '2024-04-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'ENG'), 
 'Collaborator', '2024-04-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'ENG'), 
 'Lead', '2024-07-01', NULL),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 
 (SELECT department_id FROM rmpo.departments WHERE department_code = 'BIO'), 
 'Collaborator', '2024-07-01', NULL);

-- Budget installments for all projects (using dynamic lookups)
INSERT INTO rmpo.budget_installments (project_id, installment_number, installment_date, budget_percentage, amount, payment_status, due_date) VALUES
-- Project 1: AI-Driven Genomic Analysis
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 1, '2024-01-15', 30.00, 225000.00, 'Paid', '2024-01-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 2, '2024-07-15', 35.00, 262500.00, 'Paid', '2024-07-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 3, NULL, 35.00, 262500.00, 'Pending', '2025-01-15'),
-- Project 2: Smart Campus Infrastructure
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 1, '2024-06-15', 40.00, 180000.00, 'Paid', '2024-06-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 2, NULL, 60.00, 270000.00, 'Pending', '2025-06-15'),
-- Project 3: Quantum Error Correction
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 1, '2023-09-15', 25.00, 300000.00, 'Paid', '2023-09-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 2, '2024-03-15', 30.00, 360000.00, 'Paid', '2024-03-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 3, '2024-09-15', 25.00, 300000.00, 'Paid', '2024-09-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 4, NULL, 20.00, 240000.00, 'Pending', '2025-09-15'),
-- Project 4: Sustainable Water Filtration
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 1, '2024-03-30', 35.00, 203000.00, 'Paid', '2024-03-30'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 2, '2024-09-30', 35.00, 203000.00, 'Paid', '2024-09-30'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 3, NULL, 30.00, 174000.00, 'Pending', '2025-03-30'),
-- Project 5: Climate Modeling
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 1, '2023-11-15', 30.00, 276000.00, 'Paid', '2023-11-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 2, '2024-05-15', 35.00, 322000.00, 'Paid', '2024-05-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 3, NULL, 35.00, 322000.00, 'Pending', '2024-11-15'),
-- Project 6: Green Chemistry
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 1, '2024-02-15', 30.00, 204000.00, 'Paid', '2024-02-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 2, '2024-08-15', 35.00, 238000.00, 'Paid', '2024-08-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 3, NULL, 35.00, 238000.00, 'Pending', '2025-02-15'),
-- Project 7: Neural Network Hardware
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 1, '2024-04-15', 40.00, 208000.00, 'Paid', '2024-04-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 2, NULL, 60.00, 312000.00, 'Pending', '2025-04-15'),
-- Project 8: Biomedical Sensors
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 1, '2024-07-15', 40.00, 156000.00, 'Paid', '2024-07-15'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 2, NULL, 60.00, 234000.00, 'Pending', '2025-07-15');

-- Milestones for all projects (using dynamic lookups)
INSERT INTO rmpo.milestones (project_id, milestone_name, milestone_description, planned_date, actual_date, milestone_status, completion_percentage) VALUES
-- Project 1: AI-Driven Genomic Analysis
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 'Data Collection Complete', 'Completion of genomic dataset collection and preprocessing', '2024-06-30', '2024-07-15', 'Completed', 100.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 'Algorithm Development', 'Development and testing of core ML algorithms', '2024-12-31', NULL, 'In Progress', 75.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 'System Integration', 'Integration of algorithms into analysis pipeline', '2025-06-30', NULL, 'Pending', 0.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 'Final Validation', 'Comprehensive testing and validation of the complete system', '2026-10-31', NULL, 'Pending', 0.00),
-- Project 2: Smart Campus Infrastructure
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 'Requirements Analysis', 'Complete analysis of campus infrastructure requirements', '2024-08-31', '2024-08-25', 'Completed', 100.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 'Prototype Development', 'Development of IoT sensor network prototype', '2025-02-28', NULL, 'In Progress', 45.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 'System Deployment', 'Campus-wide deployment of the monitoring system', '2026-03-31', NULL, 'Pending', 0.00),
-- Project 3: Quantum Error Correction
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 'Theoretical Framework', 'Completion of theoretical error correction framework', '2024-03-01', '2024-02-28', 'Completed', 100.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 'Algorithm Implementation', 'Implementation of error correction algorithms', '2024-12-31', NULL, 'In Progress', 60.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 'Hardware Integration', 'Integration with quantum hardware platforms', '2026-06-30', NULL, 'Pending', 0.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 'Performance Validation', 'Comprehensive performance testing and validation', '2027-06-30', NULL, 'Pending', 0.00),
-- Project 4: Sustainable Water Filtration
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 'Materials Research', 'Research and selection of sustainable filtration materials', '2024-07-15', '2024-07-10', 'Completed', 100.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 'Prototype Testing', 'Laboratory testing of filtration prototypes', '2025-01-31', NULL, 'In Progress', 30.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 'Field Trials', 'Real-world testing of filtration systems', '2025-12-31', NULL, 'Pending', 0.00),
-- Project 5: Climate Modeling
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 'Model Development', 'Development of core mathematical climate models', '2024-06-30', '2024-07-05', 'Completed', 100.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 'Validation Studies', 'Validation of models against historical data', '2025-03-31', NULL, 'In Progress', 40.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 'Regional Implementation', 'Implementation of models for specific regions', '2026-09-30', NULL, 'Pending', 0.00),
-- Project 6: Green Chemistry
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 'Process Design', 'Design of green chemistry processes', '2024-08-31', '2024-08-28', 'Completed', 100.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 'Laboratory Testing', 'Laboratory validation of green processes', '2025-06-30', NULL, 'In Progress', 35.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 'Scale-up Study', 'Industrial scale-up feasibility study', '2026-09-30', NULL, 'Pending', 0.00),
-- Project 7: Neural Network Hardware
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 'Architecture Design', 'Hardware architecture design and specification', '2024-08-31', '2024-08-20', 'Completed', 100.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 'Prototype Development', 'Development of hardware prototype', '2025-06-30', NULL, 'In Progress', 25.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 'Performance Testing', 'Comprehensive performance benchmarking', '2026-07-31', NULL, 'Pending', 0.00),
-- Project 8: Biomedical Sensors
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 'Sensor Design', 'Design and specification of biomedical sensors', '2024-10-31', NULL, 'In Progress', 70.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 'Network Protocol', 'Development of wireless communication protocols', '2025-02-28', NULL, 'Pending', 0.00),
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 'Clinical Testing', 'Clinical validation of sensor networks', '2026-04-30', NULL, 'Pending', 0.00);

-- Research outputs for all projects (using dynamic lookups)
INSERT INTO rmpo.research_outputs (project_id, output_type, output_title, publication_date, venue, description) VALUES
-- Project 1: AI-Driven Genomic Analysis
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 'Publication', 'Machine Learning Approaches to Genomic Sequence Classification', '2024-09-15', 'Journal of Computational Biology', 'Peer-reviewed article on novel ML algorithms for genomic analysis'),
((SELECT project_id FROM rmpo.projects WHERE title = 'AI-Driven Genomic Analysis'), 'Dataset', 'Preprocessed Genomic Sequences Dataset v1.0', '2024-08-01', 'University Data Repository', 'Curated dataset for ML training and validation'),
-- Project 2: Smart Campus Infrastructure
((SELECT project_id FROM rmpo.projects WHERE title = 'Smart Campus Infrastructure'), 'Report', 'Campus Infrastructure Assessment Report', '2024-09-30', 'Internal Technical Report', 'Comprehensive analysis of current campus systems and improvement recommendations'),
-- Project 3: Quantum Error Correction
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 'Publication', 'Novel Quantum Error Correction Protocols for NISQ Devices', '2024-05-20', 'Physical Review A', 'Theoretical framework for error correction in near-term quantum computers'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Quantum Error Correction Algorithms'), 'Presentation', 'Fault-Tolerant Quantum Computing: Current Challenges', '2024-03-15', 'International Conference on Quantum Computing', 'Invited presentation on quantum error correction challenges'),
-- Project 4: Sustainable Water Filtration
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 'Patent', 'Bio-based Membrane for Water Purification', '2024-08-10', 'US Patent Office', 'Patent application for novel sustainable filtration membrane'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Sustainable Water Filtration Systems'), 'Report', 'Environmental Impact Assessment of Green Filtration Technologies', '2024-09-05', 'Environmental Engineering Journal', 'Comprehensive environmental impact study'),
-- Project 5: Climate Modeling
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 'Publication', 'Advanced Mathematical Models for Regional Climate Prediction', '2024-07-30', 'Climate Dynamics', 'Mathematical approaches to regional climate modeling'),
((SELECT project_id FROM rmpo.projects WHERE title = 'Mathematical Modeling of Climate Systems'), 'Software', 'ClimatePredict Pro v2.0', '2024-06-15', 'Open Source Repository', 'Advanced climate prediction software package'),
-- Project 6: Green Chemistry
((SELECT project_id FROM rmpo.projects WHERE title = 'Green Chemistry for Drug Discovery'), 'Publication', 'Sustainable Synthesis Routes in Pharmaceutical Chemistry', '2024-09-10', 'Green Chemistry Journal', 'Review of environmentally friendly pharmaceutical synthesis methods'),
-- Project 7: Neural Network Hardware
((SELECT project_id FROM rmpo.projects WHERE title = 'Neural Network Hardware Acceleration'), 'Presentation', 'Specialized Hardware Architectures for Deep Learning', '2024-09-25', 'International Conference on Computer Architecture', 'Presentation on novel neural network acceleration hardware'),
-- Project 8: Biomedical Sensors
((SELECT project_id FROM rmpo.projects WHERE title = 'Biomedical Sensor Networks'), 'Prototype', 'Wireless Health Monitoring Sensor Network v1.0', '2024-08-30', 'University Innovation Lab', 'Functional prototype of wireless biomedical sensor system');







