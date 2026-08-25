CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';


CREATE TRIGGER update_document_modtime
BEFORE UPDATE ON documents
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();