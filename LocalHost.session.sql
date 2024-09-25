


INSERT INTO api_elementos (nombre, descripcion, tipo, enabled, simbolo, numero_atomico, masa_atomica, updated_at)
VALUES
('Cobre', 'Elemento metálico utilizado en la minería y la electricidad.', 'Metálico', TRUE, 'Cu', 29, 63.55, NOW()),
('Hierro', 'Elemento esencial en la industria de la construcción.', 'Metálico', TRUE, 'Fe', 26, 55.85, NOW()),
('Oro', 'Metal precioso utilizado en joyería y como inversión.', 'Metálico', TRUE, 'Au', 79, 196.97, NOW()),
('Plata', 'Metal valioso utilizado en joyería y electrónica.', 'Metálico', TRUE, 'Ag', 47, 107.87, NOW()),
('Aluminio', 'Elemento ligero y resistente, ampliamente usado en la industria.', 'Metálico', TRUE, 'Al', 13, 26.98, NOW()),
('Zinc', 'Metal utilizado en la galvanización y aleaciones.', 'Metálico', TRUE, 'Zn', 30, 65.38, NOW()),
('Plomo', 'Elemento pesado usado en baterías y soldaduras.', 'Metálico', TRUE, 'Pb', 82, 207.2, NOW()),
('Cromo', 'Elemento utilizado en la fabricación de acero inoxidable.', 'Metálico', TRUE, 'Cr', 24, 51.996, NOW()),
('Níquel', 'Metal utilizado en la producción de acero inoxidable y aleaciones.', 'Metálico', TRUE, 'Ni', 28, 58.69, NOW()),
('Mercurio', 'Elemento líquido a temperatura ambiente, usado en termómetros.', 'Metálico', TRUE, 'Hg', 80, 200.59, NOW()),
('Manganeso', 'Elemento utilizado en la producción de acero.', 'Metálico', TRUE, 'Mn', 25, 54.94, NOW()),
('Titanio', 'Metal ligero y resistente a la corrosión.', 'Metálico', TRUE, 'Ti', 22, 47.87, NOW()),
('Antimonio', 'Elemento usado en aleaciones y productos químicos.', 'Metálico', TRUE, 'Sb', 51, 121.76, NOW()),
('Bismuto', 'Elemento pesado utilizado en medicina y aleaciones.', 'Metálico', TRUE, 'Bi', 83, 208.98, NOW()),
('Estaño', 'Elemento utilizado en soldaduras y recubrimientos.', 'Metálico', TRUE, 'Sn', 50, 118.71, NOW()),
('Wolframio', 'Metal muy denso utilizado en lámparas y herramientas.', 'Metálico', TRUE, 'W', 74, 183.84, NOW()),
('Platino', 'Metal precioso utilizado en joyería y dispositivos electrónicos.', 'Metálico', TRUE, 'Pt', 78, 195.08, NOW()),
('Cobalto', 'Elemento utilizado en aleaciones y baterías.', 'Metálico', TRUE, 'Co', 27, 58.93, NOW()),
('Cadmio', 'Metal utilizado en baterías y recubrimientos.', 'Metálico', TRUE, 'Cd', 48, 112.41, NOW()),
('Vanadio', 'Elemento utilizado en la producción de aleaciones de acero.', 'Metálico', TRUE, 'V', 23, 50.94, NOW()),
('Lantano', 'Elemento utilizado en la fabricación de aleaciones y catalizadores.', 'Metálico', TRUE, 'La', 57, 138.91, NOW());


INSERT INTO api_analisis (Analisis_metodo, Nro_Analisis, descripcion, Formula, updated_at, enabled)
VALUES
('Análisis de Cobre', 'AN-001', 'Análisis de contenido de cobre en minerales.', 'Cu %', NOW(), TRUE),
('Análisis de Oro', 'AN-002', 'Análisis de pureza de oro en lingotes.', 'Au %', NOW(), TRUE),
('Análisis de Plomo', 'AN-003', 'Determinación de plomo en muestras.', 'Pb %', NOW(), TRUE),
('Estudio de Zinc', 'AN-004', 'Análisis de zinc en concentrados.', 'Zn %', NOW(), TRUE),
('Análisis de Hierro', 'AN-005', 'Determinación de hierro en minerales.', 'Fe %', NOW(), TRUE),
('Estudio de Aleaciones', 'AN-006', 'Análisis de aleaciones metálicas.', 'Cu + Zn', NOW(), TRUE),
('Análisis de Plata y Oro', 'AN-007', 'Contenido de plata y oro en muestras.', 'Ag + Au %', NOW(), TRUE),
('Análisis Compuesto de Manganeso', 'AN-008', 'Determinación de manganeso en aleaciones.', 'Mn %', NOW(), TRUE),
('Análisis de Cobalto y Níquel', 'AN-009', 'Estudio de contenido de cobalto y níquel.', 'Co + Ni %', NOW(), TRUE),
('Análisis Complejo', 'AN-010', 'Análisis de varios metales en minerales.', 'Cu + Pb + Zn + Fe', NOW(), TRUE);




INSERT INTO api_analisis_elementos (analisis_id, elementos_id)
VALUES
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-001'), (SELECT id FROM api_elementos WHERE nombre = 'Cobre')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-002'), (SELECT id FROM api_elementos WHERE nombre = 'Oro')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-003'), (SELECT id FROM api_elementos WHERE nombre = 'Plomo')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-004'), (SELECT id FROM api_elementos WHERE nombre = 'Zinc')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-005'), (SELECT id FROM api_elementos WHERE nombre = 'Hierro'));


INSERT INTO api_analisis_elementos (analisis_id, elementos_id)
VALUES
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-006'), (SELECT id FROM api_elementos WHERE nombre = 'Cobre')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-006'), (SELECT id FROM api_elementos WHERE nombre = 'Zinc')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-007'), (SELECT id FROM api_elementos WHERE nombre = 'Oro')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-007'), (SELECT id FROM api_elementos WHERE nombre = 'Plata')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-008'), (SELECT id FROM api_elementos WHERE nombre = 'Manganeso')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-009'), (SELECT id FROM api_elementos WHERE nombre = 'Cobalto')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-009'), (SELECT id FROM api_elementos WHERE nombre = 'Níquel')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-010'), (SELECT id FROM api_elementos WHERE nombre = 'Cobre')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-010'), (SELECT id FROM api_elementos WHERE nombre = 'Plomo')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-010'), (SELECT id FROM api_elementos WHERE nombre = 'Zinc')),
((SELECT id FROM api_analisis WHERE Nro_Analisis = 'AN-010'), (SELECT id FROM api_elementos WHERE nombre = 'Hierro'));




