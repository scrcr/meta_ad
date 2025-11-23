-- Supabase table definitions for Meta Ads pipeline

-- Utility trigger function to keep updated_at in sync.
create or replace function public.set_current_timestamp_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Ads table stores normalized ad records produced by the pipeline.
create table if not exists public.ads (
    id text primary key,
    creative_body text,
    snapshot_url text,
    page_id text,
    page_name text,
    call_to_action_type text,
    image_path text,
    ocr_text text,
    dominant_color text,
    has_person boolean,
    layout_type text,
    pitch text,
    tags text[] default '{}'::text[],
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ads_page_id_idx on public.ads (page_id);
create index if not exists ads_layout_type_idx on public.ads (layout_type);

create trigger set_ads_updated_at
before update on public.ads
for each row
execute function public.set_current_timestamp_updated_at();

-- Pages table captures newly discovered page IDs from Explore runs.
create table if not exists public.pages (
    page_id text primary key,
    created_at timestamptz not null default now()
);
