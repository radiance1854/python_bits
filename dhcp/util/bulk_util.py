from modules.dhcp import dhcp_pwsh
from modules.dhcp.util import scope_util
from modules.tools import email_util
import io
import csv

# bulk_dhcp.py

def bulk_reservation_update(reservations):

    results = []

    for reservation in reservations:

        ip = reservation["ip"]
        mac = reservation["mac"]
        description = reservation["description"]
        name = reservation["name"]
        delete = str(reservation["delete"]).lower() in ("yes", "true", "1")

        try:
            scopeId = scope_util.find_scope_for_ip(ip)
            current_reservation = dhcp_pwsh.get_reservation_for_ip(scopeId, ip)
            if delete:
                try:
                    output = dhcp_pwsh.delete_reservation_by_ip(ip)
                    results.append({"ip": ip, "status": "success", "message": output})
                except Exception as e:
                    results.append({"ip": ip, "status": "failed", "error": "Unable to delete IP reservation, it may not exist to be deleted."})
            else:
                try:
                    output = dhcp_pwsh.modify_reservation_by_ip(ip, mac, description, name)
                    results.append({"ip": ip, "status": "success", "message": output})
                except:
                    try:
                        output = dhcp_pwsh.add_reservation_by_ip(scopeId, ip, mac, description, name)
                        results.append({"ip": ip, "status": "success", "message": output})
                    except Exception as e:
                        results.append({"ip": ip, "status": "failed", "error": "Unable to add or update this IP reservation."})
        except:
            results.append({"ip": ip, "status": "failed", "error": "Unknown error for this IP reservation."})

    bulk_reservation_replication(reservations)

    return results

def bulk_reservation_replication(reservations):

    seen = set()

    for r in reservations:
        ip = r["ip"]
        try:
            scopeId = scope_util.find_scope_for_ip(ip)
            if scopeId not in seen:
                dhcp_pwsh.update_replication_for_scope(scopeId)
                seen.add(scopeId)
        except Exception:
            pass  # skip scopes that couldn't be found

# more helpers

def send_bulk_reservation_email(user_email, results, original_csv_text):
    subject = "Bulk DHCP Results"
    body = "Your Bulk DHCP request has been processed" + user_email + ". The results are: " + results
    group_email = "testtarget@domain.com"
    from_email = "noreply@domain.com"
    smtp_server = "XX.XX.XX.XX"  # SMTP server address
    smtp_port = 25  # SMTP server port

    to_email = user_email + ", " + group_email

    email_util.send_email_with_optional_attachment(smtp_server, smtp_port, from_email, to_email, subject, body, attachment_bytes=original_csv_text.encode("utf-8"), attachment_filename="bulk_input.csv")

def results_to_csv(results):
    if not results:
        return ""
    fieldnames = sorted({ key for r in results for key in r.keys() })
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(r)
    return output.getvalue()

def read_bulk_csv_data(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    reservations = [normalize_fields(row) for row in reader]
    return reservations

def normalize_fields(row):
    return {
        "ip": row["IPAddress"].strip(),
        "mac": row["MACAddress"].strip().replace(":", "-"),
        "description": row["Description"].strip(),
        "name": row["Name"].strip(),
        "delete": row["Delete"].strip(),
    }