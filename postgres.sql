
create table public.profiles (
  -- The id serves as both the Primary Key and the Foreign Key
  id uuid references auth.users on delete cascade primary key,
  first_name text,
  last_name text,
  role text not null default 'user',
  updated_at timestamp default now() not null
);


-- 1. Enable Row Level Security
alter table public.profiles enable row level security;

-- 2. Allow the 'anon' role to INSERT rows
-- (Crucial so that sign-ups don't fail when the trigger fires)
create policy "Allow public insert"
on public.profiles
for insert
to anon
with check (true);

-- 3. Allow users to read their profiles
create policy "Allow users to read their own profile"
on public.profiles
for select
to authenticated
using (auth.uid() = id);


-- USER'S PROFILE CREATING TRIGGER AT SIGN UP
create or replace function public.handle_new_user()
returns trigger as $$
declare
  user_count integer;
  assigned_role text;
begin
  -- 1. Check how many profiles currently exist in the database
  select count(*) into user_count from public.profiles;

  -- 2. Determine the role based on the count
  if user_count = 0 then
    assigned_role := 'admin';
  else
    assigned_role := 'user';
  end if;

  -- 3. Insert the concrete profile row with the determined role
  insert into public.profiles (id, first_name, last_name, role)
  values (
    new.id,
    new.raw_user_meta_data->>'first_name',
    new.raw_user_meta_data->>'last_name',
    assigned_role
  );

  return new;
end;
$$ language plpgsql security definer;

-- Drop trigger first to avoid "already exists" errors if re-running
drop trigger if exists on_auth_user_created on auth.users;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();


-- 1. CREATE HOOK FOR JWT TOKEN PAYLOAD CUSTOMIZATION
create or replace function public.custom_access_token_hook(event jsonb)
returns jsonb
language plpgsql
stable
security definer -- CRITICAL: Allows the hook to read public.profiles
set search_path = '' -- Best practice for security definer functions
as $$
declare
  current_role text;
  claims jsonb;
begin
  -- Fetch the role from your custom user profiles table
  select role into current_role 
  from public.profiles 
  where id = cast(event->>'user_id' as uuid);

  -- Isolate the claims object from the event payload
  claims := event->'claims';

  -- Inject the role directly into the claims object (Recommended pattern)
  claims := jsonb_set(claims, '{user_role}', to_jsonb(coalesce(current_role, 'user')));

  -- Update the original event payload with the modified claims object
  event := jsonb_set(event, '{claims}', claims);

  return event;
end;
$$;

-- 2. Grant permissions to the Supabase auth server to run this function
grant execute on function public.custom_access_token_hook to supabase_auth_admin;
