-- Migration: Add scheduledFor column and SCHEDULED status to orders table
-- Date: 2025-12-16
-- Description: Adds support for scheduled orders by adding scheduledFor timestamp column
--              and SCHEDULED status to OrderStatus enum

-- Add SCHEDULED status to OrderStatus enum
ALTER TYPE "OrderStatus" ADD VALUE IF NOT EXISTS 'SCHEDULED';

-- Add scheduledFor column to orders table
ALTER TABLE orders ADD COLUMN IF NOT EXISTS "scheduledFor" timestamp without time zone;

-- Add index for efficient queries on scheduled orders
CREATE INDEX IF NOT EXISTS idx_orders_scheduled ON orders("scheduledFor") WHERE "scheduledFor" IS NOT NULL;

-- Add comments for documentation
COMMENT ON COLUMN orders."scheduledFor" IS 'Timestamp for when the order should be processed (for scheduled orders)';
