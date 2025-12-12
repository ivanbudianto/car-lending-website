-- -------------------------------------------------------------
-- TablePlus 6.7.8(650)
--
-- https://tableplus.com/
--
-- Database: development.db
-- Generation Time: 2025-12-09 12:33:48.3750
-- -------------------------------------------------------------


DROP TABLE IF EXISTS "cars";
CREATE TABLE "cars" (
    id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    license_plate VARCHAR(15) NOT NULL,
    transmission_id INTEGER NOT NULL,
    image VARCHAR(128) NULL,
    status VARCHAR(30) NOT NULL,
    _inserted_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    _updated_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    _updated_by INTEGER NOT NULL DEFAULT 999,
    PRIMARY KEY (id)
);

INSERT INTO "cars" ("id", "name", "license_plate", "transmission_id", "image", "status", "_inserted_date", "_updated_date", "_updated_by") VALUES
('1', 1, 'B1111RRA', '1', NULL, 'Tersedia', '2025-12-09 00:00:08.611676', '2025-12-09 00:00:08.611676', '1'),
('2', 2, 'B1212RV', '2', NULL, 'Nonaktif', '2025-12-09 00:00:27.884060', '2025-12-09 00:00:27.884060', '1'),
('3', 3, 'F1212GG', '1', NULL, 'Tersedia', '2025-12-09 00:00:51.483821', '2025-12-09 00:00:51.483821', '1');

