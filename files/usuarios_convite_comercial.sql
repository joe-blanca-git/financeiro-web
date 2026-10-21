-- =====================================================================
-- USUARIOS POR CONVITE, NIVEL "COMERCIAL - VENDAS" e GERENTE x USUARIO
--
-- Rode este arquivo INTEIRO, de uma vez, em cada banco:
--   local e producao: deixe  USE stamariabd;
--   teste:            troque para  USE stamariabd_dev;
--
-- Pode rodar mais de uma vez sem problema. Nao apaga nenhum dado.
-- Faca backup antes de rodar na producao.
-- =====================================================================
USE stamariabd;


-- ---------------------------------------------------------------------
-- PASSO 1. Nivel de acesso "Comercial - Vendas" (so cria se nao existir)
-- ---------------------------------------------------------------------
INSERT INTO roles (name)
SELECT 'comercial_vendas'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'comercial_vendas');


-- ---------------------------------------------------------------------
-- PASSO 2. Convite em users: hash do token do link e validade (8 horas)
--          (o token em si nunca e gravado, so o hash)
-- ---------------------------------------------------------------------
SET @s = IF(
  (SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'users' AND column_name = 'convite_token_hash') = 0,
  'ALTER TABLE users ADD COLUMN convite_token_hash CHAR(64) NULL DEFAULT NULL, ADD COLUMN convite_expira_em DATETIME NULL DEFAULT NULL',
  'SELECT ''colunas de convite ja existem'' AS aviso');
PREPARE passo2 FROM @s;
EXECUTE passo2;
DEALLOCATE PREPARE passo2;


-- ---------------------------------------------------------------------
-- PASSO 3. gerente.idUser: usuario do gerente (um usuario por gerente)
-- ---------------------------------------------------------------------
SET @s = IF(
  (SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'gerente' AND column_name = 'idUser') = 0,
  'ALTER TABLE gerente ADD COLUMN idUser INT NULL DEFAULT NULL AFTER nome, ADD UNIQUE INDEX ux_gerente_idUser (idUser), ADD CONSTRAINT fk_gerente_user FOREIGN KEY (idUser) REFERENCES users (iduser)',
  'SELECT ''coluna gerente.idUser ja existe'' AS aviso');
PREPARE passo3 FROM @s;
EXECUTE passo3;
DEALLOCATE PREPARE passo3;


-- ---------------------------------------------------------------------
-- CONFERENCIA: as tres linhas devem mostrar 1
-- ---------------------------------------------------------------------
SELECT 'nivel comercial_vendas' AS item, COUNT(*) AS resultado FROM roles WHERE name = 'comercial_vendas'
UNION ALL
SELECT 'colunas de convite em users', COUNT(*) = 2 FROM information_schema.columns
  WHERE table_schema = DATABASE() AND table_name = 'users' AND column_name IN ('convite_token_hash', 'convite_expira_em')
UNION ALL
SELECT 'coluna gerente.idUser', COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE() AND table_name = 'gerente' AND column_name = 'idUser';
