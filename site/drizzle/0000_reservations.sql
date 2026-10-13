CREATE TABLE `reservations` (
  `id` text PRIMARY KEY NOT NULL,
  `reference` text NOT NULL UNIQUE,
  `customer_name` text NOT NULL,
  `phone` text NOT NULL,
  `email` text,
  `service` text NOT NULL,
  `preferred_date` text NOT NULL,
  `preferred_time` text NOT NULL,
  `alternate_date` text,
  `vehicle` text,
  `details` text NOT NULL,
  `status` text NOT NULL DEFAULT 'new',
  `admin_note` text NOT NULL DEFAULT '',
  `created_at` text NOT NULL,
  `updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `reservations_created_at_idx` ON `reservations` (`created_at`);
--> statement-breakpoint
CREATE INDEX `reservations_preferred_date_idx` ON `reservations` (`preferred_date`);
