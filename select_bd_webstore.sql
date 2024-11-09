SELECT 
    v."PEDIDO",
    v."SKU_CLIENTE",
    v."EMISSAO",
    v."PARENT",
    p."DESCRICAO_PARENT",
    v."QTD",
    v."VR_UNIT",
    v."STATUS"
FROM 
    tembo.tb_venda AS v
LEFT JOIN (
    SELECT DISTINCT ON ("PARENT") "PARENT", "DESCRICAO_PARENT"
    FROM tembo.tb_produto
    ORDER BY "PARENT"
) AS p ON v."PARENT" = p."PARENT";
