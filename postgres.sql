
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

-- 1. Clear out the old version completely
drop function if exists public.custom_access_token_hook(jsonb);

-- 2. Create the precise, isolated version
create or replace function public.custom_access_token_hook(event jsonb)
returns jsonb
language plpgsql
stable
security definer 
set search_path = ''
as $$
declare
  user_uuid uuid;
  fetched_role text;
  claims jsonb;
begin
  -- Explicitly extract and cast the user_id from the event payload
  user_uuid := cast(event->>'user_id' as uuid);

  -- Target public.profiles explicitly to prevent picking up system session info
  select public.profiles.role into fetched_role 
  from public.profiles 
  where public.profiles.id = user_uuid;

  -- Grab the existing claims object from the event payload
  claims := event->'claims';

  -- Inject the role cleanly. Coalesce ensures it defaults to 'user' if null
  claims := jsonb_set(claims, '{user_role}', to_jsonb(coalesce(fetched_role, 'user')));

  -- Overwrite only the claims sub-object in the event payload
  event := jsonb_set(event, '{claims}', claims);

  return event;
end;
$$;

-- 3. Regrant execution permission
grant execute on function public.custom_access_token_hook to supabase_auth_admin;
