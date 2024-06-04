DROP TABLE IF EXISTS robyrubirex_coderhouse.stage_api_dolarucos;

CREATE TABLE stage_api_dolarucos(
	id VARCHAR(255) PRIMARY KEY,
    moneda VARCHAR(3),
    casa VARCHAR(250),
    nombre VARCHAR(250),
    compra FLOAT,
    venta FLOAT,
    fechaActualizacion TIMESTAMP
);