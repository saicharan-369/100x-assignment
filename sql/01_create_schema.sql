-- Normalized schema for the 100x property dataset

DROP TABLE IF EXISTS taxes;
DROP TABLE IF EXISTS hoa;
DROP TABLE IF EXISTS rehab;
DROP TABLE IF EXISTS valuation;
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS property;

CREATE TABLE property (
    property_key        VARCHAR(32) PRIMARY KEY,
    property_title      VARCHAR(255) NULL,
    address             VARCHAR(255) NULL,
    market              VARCHAR(100) NULL,
    flood               VARCHAR(50) NULL,
    street_address      VARCHAR(255) NULL,
    city                VARCHAR(100) NULL,
    state               CHAR(2) NULL,
    zip_code            CHAR(5) NULL,
    property_type       VARCHAR(100) NULL,
    highway             VARCHAR(50) NULL,
    train               VARCHAR(50) NULL,
    tax_rate            DECIMAL(7,4) NULL,
    sqft_basement       INT NULL,
    htw                 VARCHAR(50) NULL,
    pool                TINYINT(1) NULL,
    commercial          TINYINT(1) NULL,
    water               VARCHAR(50) NULL,
    sewage              VARCHAR(50) NULL,
    year_built          SMALLINT NULL,
    sqft_mixed_use      INT NULL,
    sqft_total          INT NULL,
    parking             VARCHAR(50) NULL,
    bed                 TINYINT NULL,
    bath                DECIMAL(3,1) NULL,
    basement            TINYINT(1) NULL,
    layout              VARCHAR(50) NULL,
    rent_restricted     TINYINT(1) NULL,
    neighborhood_rating TINYINT NULL,
    latitude            DECIMAL(10,6) NULL,
    longitude           DECIMAL(10,6) NULL,
    subdivision         VARCHAR(255) NULL,
    school_average      DECIMAL(4,2) NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_property_address (street_address, city, state, zip_code)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE leads (
    property_key            VARCHAR(32) NOT NULL,
    reviewed_status         VARCHAR(100) NULL,
    most_recent_status      VARCHAR(100) NULL,
    source                  VARCHAR(100) NULL,
    occupancy               VARCHAR(100) NULL,
    net_yield               DECIMAL(6,3) NULL,
    irr                     DECIMAL(6,3) NULL,
    selling_reason          VARCHAR(255) NULL,
    seller_retained_broker  TINYINT(1) NULL,
    final_reviewer          VARCHAR(100) NULL,
    PRIMARY KEY (property_key),
    CONSTRAINT fk_leads_property FOREIGN KEY (property_key) REFERENCES property (property_key) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE valuation (
    property_key   VARCHAR(32) NOT NULL,
    scenario_rank  SMALLINT NOT NULL,
    list_price     DECIMAL(14,2) NULL,
    previous_rent  DECIMAL(14,2) NULL,
    arv            DECIMAL(14,2) NULL,
    expected_rent  DECIMAL(14,2) NULL,
    rent_zestimate DECIMAL(14,2) NULL,
    low_fmr        DECIMAL(14,2) NULL,
    high_fmr       DECIMAL(14,2) NULL,
    redfin_value   DECIMAL(14,2) NULL,
    zestimate      DECIMAL(14,2) NULL,
    PRIMARY KEY (property_key, scenario_rank),
    CONSTRAINT fk_valuation_property FOREIGN KEY (property_key) REFERENCES property (property_key) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE rehab (
    property_key        VARCHAR(32) NOT NULL,
    scenario_rank       SMALLINT NOT NULL,
    underwriting_rehab  DECIMAL(14,2) NULL,
    rehab_calculation   DECIMAL(14,2) NULL,
    paint               TINYINT(1) NULL,
    flooring_flag       TINYINT(1) NULL,
    foundation_flag     TINYINT(1) NULL,
    roof_flag           TINYINT(1) NULL,
    hvac_flag           TINYINT(1) NULL,
    kitchen_flag        TINYINT(1) NULL,
    bathroom_flag       TINYINT(1) NULL,
    appliances_flag     TINYINT(1) NULL,
    windows_flag        TINYINT(1) NULL,
    landscaping_flag    TINYINT(1) NULL,
    trashout_flag       TINYINT(1) NULL,
    PRIMARY KEY (property_key, scenario_rank),
    CONSTRAINT fk_rehab_property FOREIGN KEY (property_key) REFERENCES property (property_key) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE hoa (
    property_key VARCHAR(32) NOT NULL,
    scenario_rank SMALLINT NOT NULL,
    hoa_amount   DECIMAL(12,2) NULL,
    hoa_flag     TINYINT(1) NULL,
    PRIMARY KEY (property_key, scenario_rank),
    CONSTRAINT fk_hoa_property FOREIGN KEY (property_key) REFERENCES property (property_key) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE taxes (
    property_key VARCHAR(32) NOT NULL,
    amount       DECIMAL(14,2) NULL,
    PRIMARY KEY (property_key),
    CONSTRAINT fk_taxes_property FOREIGN KEY (property_key) REFERENCES property (property_key) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE INDEX idx_property_market ON property (market);
CREATE INDEX idx_property_state ON property (state);
CREATE INDEX idx_property_city ON property (city);
CREATE INDEX idx_leads_status ON leads (most_recent_status);
CREATE INDEX idx_valuation_price ON valuation (list_price);
CREATE INDEX idx_rehab_cost ON rehab (underwriting_rehab);
