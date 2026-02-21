-- Agri-Tech Platform Database Schema
-- Optimized for Supabase (PostgreSQL)
-- Core tables for Farmers, Experts, and Agricultural Intelligence

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users
-- id (uuid) | name | phone | role (farmer/expert/admin) | language_pref | created_at
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    phone TEXT,
    role TEXT CHECK (role IN ('farmer', 'expert', 'admin')),
    language_pref TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Crops
-- id | name | category | season_start | season_end | soil_types (json) | irrigation (text) | pests (json) | fertilizer_schedule (json) | sample_images
CREATE TABLE IF NOT EXISTS public.crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    category TEXT,
    season_start TEXT,
    season_end TEXT,
    soil_types JSONB, -- Array of soil types
    irrigation TEXT,
    pests JSONB, -- Common pests and solutions
    fertilizer_schedule JSONB,
    sample_images TEXT[], -- URLs to crop images
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Posts (Community Forum)
-- id | user_id | crop_id (nullable) | title | body | tags | replies_count | created_at
CREATE TABLE IF NOT EXISTS public.posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    crop_id UUID REFERENCES public.crops(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    tags TEXT[],
    replies_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Replies
-- id | post_id | user_id | body | is_expert | created_at
CREATE TABLE IF NOT EXISTS public.replies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES public.posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    is_expert BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Mandi Rates
-- id | district | market | crop_id | date | min_price | max_price | avg_price | source
CREATE TABLE IF NOT EXISTS public.mandi_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    district TEXT NOT NULL,
    market TEXT NOT NULL,
    crop_id UUID REFERENCES public.crops(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    min_price NUMERIC,
    max_price NUMERIC,
    avg_price NUMERIC,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Transport Requests
-- id | user_id | crop_id | qty | pickup_latlon | drop_latlon | preferred_date | status | assigned_to
CREATE TABLE IF NOT EXISTS public.transport_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    crop_id UUID REFERENCES public.crops(id) ON DELETE CASCADE,
    qty TEXT, -- Quantity with units (e.g., "500kg")
    pickup_latlon TEXT, -- Coordinate string or address
    drop_latlon TEXT,
    preferred_date DATE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'in-transit', 'completed', 'cancelled')),
    assigned_to UUID REFERENCES public.users(id), -- Reference to driver/expert/admin
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Recommendations Log (AI/Expert insights)
-- id | input_json | output_json | model_version | created_at
CREATE TABLE IF NOT EXISTS public.recommendations_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    input_json JSONB,
    output_json JSONB,
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crops ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.replies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mandi_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transport_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations_log ENABLE ROW LEVEL SECURITY;

-- Basic Policies (Public read for crops/mandi, Auth for others)
CREATE POLICY "Public can view crops" ON public.crops FOR SELECT USING (true);
CREATE POLICY "Public can view mandi rates" ON public.mandi_rates FOR SELECT USING (true);
CREATE POLICY "Users can view all posts" ON public.posts FOR SELECT USING (true);
CREATE POLICY "Users can view all replies" ON public.replies FOR SELECT USING (true);
CREATE POLICY "Users can manage their own posts" ON public.posts FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own profile" ON public.users FOR ALL USING (auth.uid() = id);
