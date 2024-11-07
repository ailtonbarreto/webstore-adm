SELECT 
    tembo.tb_venda."PEDIDO", 
    tembo.tb_venda."EMISSAO", 
    tembo.tb_venda."PARENT", 
	tembo.tb_venda."QTD",
	tembo.tb_venda."VR_UNIT",
	tembo.tb_venda."STATUS",
    tembo.tb_venda."SKU_CLIENTE", 
    tembo.tb_cliente."CLIENTE", 
    tembo.tb_produto."DESCRICAO"
FROM tembo.tb_venda JOIN tembo.tb_cliente ON tembo.tb_venda."SKU_CLIENTE" = tembo.tb_cliente."SKU_CLIENTE"
JOIN tembo.tb_produto ON tembo.tb_venda."PARENT" = tembo.tb_produto."PARENT";


