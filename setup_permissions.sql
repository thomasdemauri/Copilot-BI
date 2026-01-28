-- =====================================================
-- Script para conceder permissões ao usuário agent_bi
-- Executar como root no MySQL
-- =====================================================

-- 1. Criar usuário se não existir (opcional)
-- CREATE USER 'agent_bi'@'%' IDENTIFIED BY 'sua_senha_aqui';

-- 2. Conceder todas as permissões no database Olist
GRANT ALL PRIVILEGES ON Olist.* TO 'agent_bi'@'%';

-- 3. Conceder permissões para criar tabelas
GRANT CREATE ON Olist.* TO 'agent_bi'@'%';

-- 4. Conceder permissões para modificar dados
GRANT SELECT, INSERT, UPDATE, DELETE ON Olist.* TO 'agent_bi'@'%';

-- 5. Recarregar as permissões
FLUSH PRIVILEGES;

-- 6. Verificar as permissões (opcional)
-- SHOW GRANTS FOR 'agent_bi'@'%';

-- =====================================================
-- Alternativa: Se quiser permissões totais
-- =====================================================
-- GRANT ALL PRIVILEGES ON *.* TO 'agent_bi'@'%' WITH GRANT OPTION;
-- FLUSH PRIVILEGES;

-- =====================================================
-- Para verificar se funcionou
-- =====================================================
-- mysql -u agent_bi -p -h localhost
-- USE Olist;
-- SHOW TABLES;
