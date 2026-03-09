-- Добавление связи discounts -> campaigns
-- Выполнять после create_campaigns_table.sql

ALTER TABLE discounts
    ADD COLUMN IF NOT EXISTS campaign_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'discounts_campaign_id_fkey'
          AND table_name = 'discounts'
    ) THEN
        ALTER TABLE discounts
            ADD CONSTRAINT discounts_campaign_id_fkey
            FOREIGN KEY (campaign_id)
            REFERENCES campaigns(id)
            ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_discount_campaign_id
    ON discounts(campaign_id)
    WHERE campaign_id IS NOT NULL;
