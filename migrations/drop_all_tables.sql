/* =========================================================
   DROP ALL TABLES - CLEAN SLATE
   Database: departments
   Use this to completely reset the database
   ========================================================= */

-- Drop all tables in reverse dependency order (OLD + NEW)
DROP TABLE IF EXISTS incidents CASCADE;
DROP TABLE IF EXISTS reservoirs CASCADE;
DROP TABLE IF EXISTS pipelines CASCADE;
DROP TABLE IF EXISTS workers CASCADE;
DROP TABLE IF EXISTS work_schedules CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS department_budgets CASCADE;
DROP TABLE IF EXISTS agent_decisions CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- Drop OLD tables from previous schemas
DROP TABLE IF EXISTS agent_messages CASCADE;
DROP TABLE IF EXISTS budgets CASCADE;
DROP TABLE IF EXISTS emergency_incidents CASCADE;
DROP TABLE IF EXISTS fire_stations CASCADE;
DROP TABLE IF EXISTS manpower CASCADE;
DROP TABLE IF EXISTS negotiation_logs CASCADE;
DROP TABLE IF EXISTS resources CASCADE;
DROP TABLE IF EXISTS water_incidents CASCADE;
DROP TABLE IF EXISTS water_infrastructure CASCADE;
DROP TABLE IF EXISTS water_resources CASCADE;

-- Drop the update trigger function if it exists
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '====================================================';
    RAISE NOTICE '✅ ALL TABLES DROPPED SUCCESSFULLY!';
    RAISE NOTICE '====================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Tables removed:';
    RAISE NOTICE '   ✓ incidents';
    RAISE NOTICE '   ✓ reservoirs';
    RAISE NOTICE '   ✓ pipelines';
    RAISE NOTICE '   ✓ workers';
    RAISE NOTICE '   ✓ work_schedules';
    RAISE NOTICE '   ✓ projects';
    RAISE NOTICE '   ✓ department_budgets';
    RAISE NOTICE '   ✓ agent_decisions';
    RAISE NOTICE '   ✓ departments';
    RAISE NOTICE '   ✓ agent_messages (old)';
    RAISE NOTICE '   ✓ budgets (old)';
    RAISE NOTICE '   ✓ emergency_incidents (old)';
    RAISE NOTICE '   ✓ fire_stations (old)';
    RAISE NOTICE '   ✓ manpower (old)';
    RAISE NOTICE '   ✓ negotiation_logs (old)';
    RAISE NOTICE '   ✓ resources (old)';
    RAISE NOTICE '   ✓ water_incidents (old)';
    RAISE NOTICE '   ✓ water_infrastructure (old)';
    RAISE NOTICE '   ✓ water_resources (old)';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions removed:';
    RAISE NOTICE '   ✓ update_updated_at_column()';
    RAISE NOTICE '';
    RAISE NOTICE '🧹 Database is now clean!';
    RAISE NOTICE '====================================================';
END $$;
