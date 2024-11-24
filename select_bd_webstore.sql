SELECT 
    cp."PARENT",
    p."SKU",
    p."DESCRICAO",
    cp."IMAGEM",
    cp."CATEGORIA",
    cp."VR_UNIT",
    cp."DESCRICAO_PARENT"
FROM 
    tembo.tb_produto AS p
JOIN 
    tembo.tb_produto_parent AS cp
ON 
    p."PARENT" = cp."PARENT";
