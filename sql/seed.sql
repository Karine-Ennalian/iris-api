-- Dados 100% fictícios para desenvolvimento e apresentação do TCC.
-- Execute depois de schema.sql.

insert into health_units (id, name, type, address, neighborhood, phone, latitude, longitude)
values
('11111111-1111-1111-1111-111111111111', 'Unidade de Saúde Íris Centro', 'UBS', 'Rua Exemplo, 100', 'Centro', '8530000001', -3.7319, -38.5267),
('22222222-2222-2222-2222-222222222222', 'Unidade de Saúde Íris Aldeota', 'UBS', 'Av. Exemplo, 200', 'Aldeota', '8530000002', -3.7350, -38.5000)
on conflict (id) do nothing;

insert into patients (id, cns, cpf, name, birth_date, phone, email, address, health_unit_id)
values
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '123456789012345', '12345678900', 'Maria da Silva', '1995-04-18', '85999999942', 'maria@example.test', 'Rua Fictícia, 10', '11111111-1111-1111-1111-111111111111'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '987654321098765', '98765432100', 'João Oliveira', '1988-11-02', '85988888877', 'joao@example.test', 'Av. Fictícia, 20', '22222222-2222-2222-2222-222222222222')
on conflict (id) do nothing;

insert into appointment_slots (id, specialty, professional_name, health_unit_id, appointment_date, appointment_time, available)
values
('30000000-0000-0000-0000-000000000001', 'Cardiologia', 'Dra. Ana Lima', '11111111-1111-1111-1111-111111111111', current_date + 7, '09:00', true),
('30000000-0000-0000-0000-000000000002', 'Cardiologia', 'Dra. Ana Lima', '11111111-1111-1111-1111-111111111111', current_date + 7, '14:30', true),
('30000000-0000-0000-0000-000000000003', 'Clínica Geral', 'Dr. Bruno Costa', '22222222-2222-2222-2222-222222222222', current_date + 9, '08:00', true)
on conflict (id) do nothing;

insert into appointments (id, patient_id, specialty, professional_name, health_unit_id, appointment_date, appointment_time, status)
values
('40000000-0000-0000-0000-000000000001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Cardiologia', 'Dra. Ana Lima', '11111111-1111-1111-1111-111111111111', current_date + 14, '14:30', 'scheduled')
on conflict (id) do nothing;

insert into exams (id, patient_id, exam_type, request_date, scheduled_date, status, health_unit_name, preparation, result_text, result_url)
values
('50000000-0000-0000-0000-000000000001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Hemograma', current_date - 10, current_date - 7, 'result_available', 'Unidade de Saúde Íris Centro', 'Jejum não obrigatório.', 'Resultado fictício disponível para demonstração acadêmica.', null),
('50000000-0000-0000-0000-000000000002', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Ultrassonografia', current_date - 3, current_date + 4, 'scheduled', 'Unidade de Saúde Íris Aldeota', 'Beber água conforme orientação da unidade.', null, null)
on conflict (id) do nothing;

insert into vaccines (id, patient_id, vaccine_name, dose, application_date, status, health_unit_name)
values
('60000000-0000-0000-0000-000000000001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Influenza', 'Dose anual', null, 'pending', null),
('60000000-0000-0000-0000-000000000002', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Hepatite B', '2ª dose', current_date - 365, 'completed', 'Unidade de Saúde Íris Centro')
on conflict (id) do nothing;

insert into medications (id, name, dosage, presentation)
values
('70000000-0000-0000-0000-000000000001', 'Losartana', '50 mg', 'Comprimido'),
('70000000-0000-0000-0000-000000000002', 'Metformina', '500 mg', 'Comprimido')
on conflict (id) do nothing;

insert into medication_stock (id, medication_id, health_unit_id, quantity)
values
('80000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 42),
('80000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 8),
('80000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', 75)
on conflict (id) do nothing;
