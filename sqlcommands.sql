-- --------------------
-- SCHEMA CREATION
-- --------------------

-- Station Table
CREATE TABLE Station (
    station_id INT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL UNIQUE,
    city VARCHAR(100),
    state VARCHAR(100)
);

-- Train Table
CREATE TABLE Train (
    train_id INT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    train_type VARCHAR(50) CHECK (train_type IN ('Express', 'Passenger', 'Goods')),
    total_coaches INT DEFAULT 10
);

-- Route Table
CREATE TABLE Route (
    route_id INT PRIMARY KEY,
    train_id INT,
    station_id INT,
    arrival_time TIME,
    departure_time TIME,
    day INT CHECK (day > 0),
    station_order INT,
    FOREIGN KEY (train_id) REFERENCES Train(train_id) ON DELETE CASCADE,
    FOREIGN KEY (station_id) REFERENCES Station(station_id),
    UNIQUE (train_id, station_order)
);

-- Passenger Table
CREATE TABLE Passenger (
    passenger_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    age INT CHECK (age > 0),
    email VARCHAR(100) UNIQUE,
    phone_number CHAR(10) UNIQUE
);

-- Ticket Table
CREATE TABLE Ticket (
    ticket_id INT PRIMARY KEY,
    passenger_id INT,
    train_id INT,
    journey_date DATE,
    seat_number VARCHAR(10),
    class VARCHAR(10) CHECK (class IN ('SL', '3A', '2A', '1A')),
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (passenger_id) REFERENCES Passenger(passenger_id),
    FOREIGN KEY (train_id) REFERENCES Train(train_id),
    UNIQUE (train_id, journey_date, seat_number)
);

-- Payment Table
CREATE TABLE Payment (
    payment_id INT PRIMARY KEY,
    ticket_id INT UNIQUE,
    amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id)
);

-- --------------------
-- TRIGGERS
-- --------------------

DELIMITER $$

CREATE TRIGGER prevent_past_booking
BEFORE INSERT ON Ticket
FOR EACH ROW
BEGIN
    IF NEW.journey_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Journey date cannot be in the past';
    END IF;
END$$

DELIMITER ;

-- --------------------
-- INDEXING
-- --------------------

CREATE INDEX idx_route_train ON Route(train_id);
CREATE INDEX idx_ticket_journey ON Ticket(train_id, journey_date);

-- --------------------
-- INSERT DATA
-- --------------------

-- Insert into Station
INSERT INTO Station (station_id, station_name, city, state) VALUES
(1, 'Howrah Junction', 'Howrah', 'West Bengal'),
(2, 'Chennai Central', 'Chennai', 'Tamil Nadu'),
(3, 'New Delhi', 'New Delhi', 'Delhi'),
(4, 'Mumbai CST', 'Mumbai', 'Maharashtra'),
(5, 'Secunderabad', 'Hyderabad', 'Telangana');

-- Insert into Train
INSERT INTO Train (train_id, train_name, train_type, total_coaches) VALUES
(101, 'Duronto Express', 'Express', 18),
(102, 'Chennai Express', 'Express', 22),
(103, 'Rajdhani Express', 'Express', 20),
(104, 'Shatabdi Express', 'Express', 16),
(105, 'Goods Carrier 1', 'Goods', 40);

-- Insert into Route
INSERT INTO Route (route_id, train_id, station_id, arrival_time, departure_time, day, station_order) VALUES
(1, 101, 1, '08:00:00', '08:15:00', 1, 1),
(2, 101, 3, '20:00:00', '20:15:00', 1, 2),
(3, 102, 2, '06:00:00', '06:20:00', 1, 1),
(4, 102, 4, '14:30:00', '14:45:00', 1, 2),
(5, 103, 3, '07:00:00', '07:30:00', 1, 1);

-- Insert into Passenger
INSERT INTO Passenger (passenger_id, name, gender, age, email, phone_number) VALUES
(201, 'Rahul Verma', 'M', 28, 'rahul.verma@gmail.com', '9876543210'),
(202, 'Sneha Iyer', 'F', 25, 'sneha.iyer@yahoo.com', '8765432109'),
(203, 'Amit Sharma', 'M', 35, 'amit.sharma@outlook.com', '7654321098'),
(204, 'Pooja Rani', 'F', 30, 'pooja.rani@gmail.com', '9988776655'),
(205, 'Karan Mehta', 'M', 22, 'karan.mehta@gmail.com', '8899001122');

-- Insert into Ticket
INSERT INTO Ticket (ticket_id, passenger_id, train_id, journey_date, seat_number, class) VALUES
(301, 201, 101, '2025-05-10', 'S1-23', 'SL'),
(302, 202, 102, '2025-05-11', '3A-15', '3A'),
(303, 203, 103, '2025-05-12', '2A-05', '2A'),
(304, 204, 101, '2025-05-10', 'S2-10', 'SL'),
(305, 205, 104, '2025-05-13', 'CC-03', '2A');

-- Insert into Payment
INSERT INTO Payment (payment_id, ticket_id, amount, payment_method, payment_date) VALUES
(401, 301, 550.00, 'UPI', '2025-04-30 12:00:00'),
(402, 302, 1250.00, 'Credit Card', '2025-04-30 12:05:00'),
(403, 303, 1550.00, 'Net Banking', '2025-04-30 12:10:00'),
(404, 304, 550.00, 'UPI', '2025-04-30 12:15:00'),
(405, 305, 750.00, 'Debit Card', '2025-04-30 12:20:00');

-- --------------------
-- VIEWS
-- --------------------

CREATE VIEW Upcoming_Schedules AS
SELECT T.train_name, S.station_name, R.arrival_time, R.departure_time, R.day
FROM Train T
JOIN Route R ON T.train_id = R.train_id
JOIN Station S ON R.station_id = S.station_id
WHERE R.day >= 1
ORDER BY T.train_name, R.day, R.station_order;

CREATE VIEW Passenger_Bookings AS
SELECT P.name AS Passenger_Name, T.train_name, TK.journey_date, TK.seat_number, TK.class
FROM Passenger P
JOIN Ticket TK ON P.passenger_id = TK.passenger_id
JOIN Train T ON TK.train_id = T.train_id;

-- --------------------
-- SELECT STATEMENTS FOR VERIFICATION
-- --------------------

-- View train schedules
SELECT * FROM Upcoming_Schedules;

-- View passenger bookings
SELECT * FROM Passenger_Bookings;
