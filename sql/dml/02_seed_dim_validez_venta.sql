INSERT INTO dwh.dim_validez_venta (
    sk_validez, tiene_factura, tiene_nota_credito, es_venta_valida, descripcion
) VALUES
    (1, TRUE,  FALSE, TRUE,  'Venta valida'),
    (2, FALSE, FALSE, FALSE, 'Sin factura'),
    (3, TRUE,  TRUE,  FALSE, 'Con nota credito'),
    (4, FALSE, TRUE,  FALSE, 'Sin factura con nota credito')
ON CONFLICT (sk_validez) DO NOTHING;
