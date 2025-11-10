


INSERT INTO api_cliente (nombre_empresa, rut, direccion, telefono, email)
VALUES
('Minera Cerro Águila', '76.345.128-9', 'Av. Cordillera 3450, Antofagasta', '+56 9 8765 4321', 'contacto@cerroaguila.cl'),

('Sociedad Minera Andina del Sur', '80.221.468-1', 'Ruta 5 Norte Km 720, Calama', '+56 9 7654 3210', 'info@andinasur.cl'),

('Exploraciones Norte Verde', '79.587.219-0', 'Camino Quebrada Seca 2100, Copiapó', '+56 9 9988 7766', 'contacto@norteverde.cl'),

('Minerales del Desierto Ltda.', '77.451.239-4', 'Parque Industrial La Chimba 154, Antofagasta', '+56 9 9123 5644', 'administracion@desiertoltda.cl'),

('Compañía Minera Altavista', '78.412.569-7', 'Av. Los Mineros 450, Iquique', '+56 9 8762 5533', 'soporte@altavista.cl');


INSERT INTO api_proyecto (nombre, cliente_id, fecha_emision)
VALUES
('Proyecto Geotécnico Cerro Águila 2025', 1, '2025-02-15'),
('Campaña de Muestreo Zona Norte', 1, '2025-04-10'),

('Estudio Hidrogeológico Quebrada Alta', 2, '2025-03-22'),
('Evaluación de Riesgo Operacional 2025', 2, '2025-05-11'),

('Sondajes Exploratorios Sector Norte Verde', 3, '2025-01-30'),

('Levantamiento Topográfico Sector Desierto Norte', 4, '2025-02-18'),

('Proyecto de Monitoreo Ambiental Altavista', 5, '2025-06-07');


INSERT INTO api_elementos (nombre, gramos, miligramos)
VALUES
('Cobre (Cu)', 12.5, 12500),
('Manganeso (Mn)', 8.2, 8200),
('Hierro (Fe)', 15.0, 15000),
('Níquel (Ni)', 4.7, 4700),
('Zinc (Zn)', 9.3, 9300),
('Plomo (Pb)', 2.1, 2100),
('Molibdeno (Mo)', 3.8, 3800),
('Aluminio (Al)', 11.1, 11100),
('Silicio (Si)', 5.6, 5600),
('Arsénico (As)', 1.4, 1400);


INSERT INTO api_metodoanalisis (cliente_id, nombre, metodologia)
VALUES
(1, 'Análisis de Concentración de Metales', 'Determinación de concentración de metales pesados mediante espectrometría de absorción atómica (AAS). Preparación mediante digestión ácida y medición comparativa con estándares certificados.'),

(2, 'Método de Identificación Química Rápida', 'Proceso de identificación cualitativa basado en reactividad a agentes químicos estándar. Incluye separación por filtrado y prueba colorimétrica.'),

(3, 'Ensayo de Pureza de Materiales', 'Evaluación del nivel de pureza mediante espectrometría ICP-OES. El muestreo se realiza en ambiente controlado con calibración por patrones internos.'),

(4, 'Cuantificación por Rayos X (FRX)', 'Método basado en fluorescencia de rayos X para determinar la composición elemental sin destrucción de la muestra.');

INSERT INTO api_metodoanalisis_elementos (metodoanalisis_id, elementos_id)
VALUES
-- Método 1: Análisis de Metales (3 elementos)
(1, 1), -- Cobre
(1, 3), -- Hierro
(1, 5), -- Zinc

-- Método 2: Identificación Química (3 elementos)
(2, 2), -- Manganeso
(2, 8), -- Aluminio
(2, 10), -- Arsénico

-- Método 3: Ensayo de Pureza (2 elementos)
(3, 4), -- Níquel
(3, 7), -- Molibdeno

-- Método 4: FRX (3 elementos)
(4, 6), -- Plomo
(4, 9), -- Silicio
(4, 1); -- Cobre



INSERT INTO api_parametros (Unidad, VA, DS, Min, Max)
VALUES
('mg/L', 12.4, 0.8, 10.0, 15.0),
('mg/kg', 8.1, 0.5, 6.0, 9.5),
('µg/L', 2.5, 0.2, 1.5, 3.0),
('ppm', 45.0, 2.1, 40.0, 50.0),
('%', 0.82, 0.03, 0.75, 0.90),
('mg/L', 5.6, 0.4, 4.0, 6.0);


INSERT INTO api_parametros_elementos (parametros_id, elementos_id)
VALUES
-- Parámetro 1
(1, 1),  -- Cobre
(1, 3),  -- Hierro
(1, 5),  -- Zinc

-- Parámetro 2
(2, 2),  -- Manganeso
(2, 7),  -- Molibdeno

-- Parámetro 3
(3, 10), -- Arsénico
(3, 4),  -- Níquel
(3, 6),  -- Plomo

-- Parámetro 4
(4, 1),  -- Cobre
(4, 8),  -- Aluminio

-- Parámetro 5
(5, 9),  -- Silicio
(5, 3),  -- Hierro
(5, 2),  -- Manganeso

-- Parámetro 6
(6, 4),  -- Níquel
(6, 6);  -- Plomo


INSERT INTO api_estandar (Nombre, cliente_id)
VALUES
('Estandar A1', 1),
('Estandar A2', 1),
('Estandar B1', 2),
('Estandar C1', 3),
('Estandar D1', 4);


-- Estandar A1 → 3 parámetros
INSERT INTO api_estandar_parametros (estandar_id, parametros_id)
VALUES
(1, 1),
(1, 3),
(1, 5);

-- Estandar A2 → 4 parámetros
INSERT INTO api_estandar_parametros (estandar_id, parametros_id)
VALUES
(2, 2),
(2, 4),
(2, 6),
(2, 7);

-- Estandar B1 → 2 parámetros
INSERT INTO api_estandar_parametros (estandar_id, parametros_id)
VALUES
(3, 1),
(3, 8);

-- Estandar C1 → 4 parámetros
INSERT INTO api_estandar_parametros (estandar_id, parametros_id)
VALUES
(4, 3),
(4, 5),
(4, 7),
(4, 9);

-- Estandar D1 → 1 parámetro
INSERT INTO api_estandar_parametros (estandar_id, parametros_id)
VALUES
(5, 10);
