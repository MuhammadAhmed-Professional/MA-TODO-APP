SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE '%user%' OR table_name LIKE '%session%' OR table_name LIKE '%auth%'
ORDER BY table_name;
