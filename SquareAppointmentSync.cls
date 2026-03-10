public with sharing class SquareAppointmentSync {
    public class SquareApiException extends Exception {}

    /**
     * Pulls one booking from Square and creates a Salesforce Event.
     *
     * Prerequisites:
     * 1) Create a Named Credential called "Square" that points to https://connect.squareup.com
     * 2) Auth must include an access token with Bookings read access.
     */
    @AuraEnabled
    public static Id createAppointmentFromSquare(String bookingId, Id ownerId) {
        if (String.isBlank(bookingId)) {
            throw new SquareApiException('bookingId is required.');
        }

        SquareBooking booking = fetchBooking(bookingId);
        Event appt = mapBookingToEvent(booking, ownerId);
        insert appt;
        return appt.Id;
    }

    @TestVisible
    private static SquareBooking fetchBooking(String bookingId) {
        HttpRequest req = new HttpRequest();
        req.setMethod('GET');
        req.setEndpoint('callout:Square/v2/bookings/' + EncodingUtil.urlEncode(bookingId, 'UTF-8'));
        req.setHeader('Content-Type', 'application/json');

        HttpResponse res = new Http().send(req);
        Integer status = res.getStatusCode();

        if (status < 200 || status >= 300) {
            throw new SquareApiException(
                'Square request failed. Status=' + status + ', body=' + res.getBody()
            );
        }

        SquareBookingEnvelope envelope =
            (SquareBookingEnvelope) JSON.deserialize(res.getBody(), SquareBookingEnvelope.class);

        if (envelope == null || envelope.booking == null) {
            throw new SquareApiException('Square response did not include a booking payload.');
        }

        return envelope.booking;
    }

    @TestVisible
    private static Event mapBookingToEvent(SquareBooking booking, Id ownerId) {
        if (booking == null || String.isBlank(booking.start_at)) {
            throw new SquareApiException('Booking payload is missing required start_at field.');
        }

        Datetime startDt = parseIso8601(booking.start_at);
        Integer durationMins = 30;

        if (booking.appointment_segments != null && !booking.appointment_segments.isEmpty()) {
            Integer total = 0;
            for (SquareAppointmentSegment seg : booking.appointment_segments) {
                if (seg != null && seg.duration_minutes != null && seg.duration_minutes > 0) {
                    total += seg.duration_minutes;
                }
            }
            if (total > 0) {
                durationMins = total;
            }
        }

        Event appt = new Event();
        appt.OwnerId = (ownerId == null ? UserInfo.getUserId() : ownerId);
        appt.Subject = String.isBlank(booking.location_id)
            ? 'Square Booking ' + booking.id
            : 'Square Booking ' + booking.id + ' (' + booking.location_id + ')';
        appt.StartDateTime = startDt;
        appt.EndDateTime = startDt.addMinutes(durationMins);

        String description =
            'Square Booking\n' +
            'Booking Id: ' + booking.id + '\n' +
            'Customer Id: ' + booking.customer_id + '\n' +
            'Location Id: ' + booking.location_id + '\n' +
            'Status: ' + booking.status;
        appt.Description = description;

        return appt;
    }

    @TestVisible
    private static Datetime parseIso8601(String value) {
        // Example from Square: 2026-01-11T17:00:00Z
        String normalized = value != null ? value.replace('T', ' ').replace('Z', '') : null;
        return Datetime.valueOfGmt(normalized);
    }

    public class SquareBookingEnvelope {
        public SquareBooking booking;
    }

    public class SquareBooking {
        public String id;
        public String status;
        public String start_at;
        public String location_id;
        public String customer_id;
        public List<SquareAppointmentSegment> appointment_segments;
    }

    public class SquareAppointmentSegment {
        public Integer duration_minutes;
        public String service_variation_id;
        public String team_member_id;
    }
}
