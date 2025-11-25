
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    role ENUM('patient','provider','admin') DEFAULT 'patient',
    dob DATE,
    gender ENUM('male','female','other'),
    language_pref VARCHAR(10) DEFAULT 'en',
    is_verified BOOLEAN DEFAULT FALSE,
    google_id VARCHAR(255),
    refresh_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO ai_chats (
    user_id,
    input_text,
    ai_response,
    summary,
    red_flag,
    photo_url,
    created_at
) VALUES (
    1,  -- linked patient (FK → users.id)
    'I have a skin rash on my arm',  -- user message
    'Based on your description, it may be an allergic reaction. Please consult a dermatologist.', -- AI response
    'Possible allergic rash, needs dermatologist review', -- AI-generated summary
    TRUE,  -- flagged for clinician
    'https://example.com/uploads/rash_photo.jpg', -- optional uploaded image
    NOW()  -- created time
);
CREATE TABLE cases (
    id INT AUTO_INCREMENT PRIMARY KEY,                          -- Case ID
    user_id INT NOT NULL,                                       -- Linked patient (FK → users.id)
    ai_chat_id INT,                                             -- Originating chat (nullable, FK → ai_chats.id)
    title VARCHAR(255) NOT NULL,                                -- Case name (e.g., “Skin rash on arm”)
    symptoms TEXT,                                              -- Captured form data
    photos JSON,                                                -- Array of URLs
    status ENUM('open','in_progress','closed') DEFAULT 'open',  -- Case lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,             -- Created timestamp
    
    CONSTRAINT fk_case_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_case_chat FOREIGN KEY (ai_chat_id) REFERENCES ai_chats(id)
);



CREATE TABLE consent_type (
    id INT AUTO_INCREMENT PRIMARY KEY,                        
    user_id INT NOT NULL,                                     
    consent_type ENUM('privacy','terms','parental') NOT NULL, 
    status ENUM('accepted','rejected') NOT NULL,              
    accepted_on DATETIME NOT NULL,                           
    
    CONSTRAINT fk_consent_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE providers (
    id INT AUTO_INCREMENT PRIMARY KEY,                  -- Provider ID
    user_id INT NOT NULL,                               -- Linked user account
    license_number VARCHAR(100) NOT NULL,               -- Govt license / registration number
    verification_status ENUM('pending','verified','rejected') DEFAULT 'pending', -- KYC status
    specialty VARCHAR(100),                             -- e.g., 'Dermatologist'
    experience_years INT,                               -- Experience in years
    languages JSON,                                     -- e.g., ["English","Telugu"]
    consultation_fee DECIMAL(10,2),                     -- Base fee
    bio TEXT,                                           -- Short professional summary
    profile_photo VARCHAR(255),                         -- URL path for profile photo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Record creation time
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);
alter table providers add column name varchar(255) after user_id;


CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,                           -- Payment record ID
    user_id INT NOT NULL,                                        -- Who paid (FK → users.id)
    appointment_id INT NOT NULL,                                 -- Linked appointment (FK → appointments.id)
    amount DECIMAL(10,2) NOT NULL,                               -- Paid amount
    currency VARCHAR(10) NOT NULL,                               -- e.g., INR
    status ENUM('initiated','success','failed','refunded') 
           DEFAULT 'initiated',                                  -- Payment state
    gateway_txn_id VARCHAR(100) NOT NULL,                        -- Razorpay txn ID
    refund_status ENUM('none','requested','processed') 
           DEFAULT 'none',                                       -- Refund status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,              -- Created timestamp

    -- Foreign Keys
    CONSTRAINT fk_payment_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_payment_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);


CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,                           -- Appointment ID
    case_id INT NOT NULL,                                        -- Linked case (FK → cases.id)
    patient_id INT NOT NULL,                                     -- Patient (FK → users.id)
    provider_id INT NOT NULL,                                    -- Clinician (FK → providers.id)
    preferred_slot DATETIME NOT NULL,                            -- Requested slot
    confirmed_slot DATETIME,                                     -- Confirmed time (nullable until confirmed)
    status ENUM('pending','confirmed','completed','cancelled') 
           DEFAULT 'pending',                                    -- Appointment state
    video_link VARCHAR(255),                                     -- Secure consultation link
    payment_id INT,                                              -- Linked payment record (FK → payments.id)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,              -- Created timestamp

    -- Foreign Keys
    CONSTRAINT fk_appointment_case FOREIGN KEY (case_id) REFERENCES cases(id),
    CONSTRAINT fk_appointment_patient FOREIGN KEY (patient_id) REFERENCES users(id),
    CONSTRAINT fk_appointment_provider FOREIGN KEY (provider_id) REFERENCES providers(id),
    CONSTRAINT fk_appointment_payment FOREIGN KEY (payment_id) REFERENCES payments(id)
);
