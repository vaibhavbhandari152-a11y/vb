@IsTest
private class SquareAppointmentSyncTest {
    private class SquareBookingMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            System.assertEquals('GET', req.getMethod());
            System.assert(req.getEndpoint().contains('/v2/bookings/BK-123'));

            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            res.setHeader('Content-Type', 'application/json');
            res.setBody('{"booking":{"id":"BK-123","status":"ACCEPTED","start_at":"2026-01-11T17:00:00Z","location_id":"LOC-1","customer_id":"CUST-1","appointment_segments":[{"duration_minutes":45}]}}');
            return res;
        }
    }

    @IsTest
    static void createsEventFromSquareBooking() {
        Test.setMock(HttpCalloutMock.class, new SquareBookingMock());

        Test.startTest();
        Id eventId = SquareAppointmentSync.createAppointmentFromSquare('BK-123', UserInfo.getUserId());
        Test.stopTest();

        Event insertedEvent = [
            SELECT Id, Subject, StartDateTime, EndDateTime, Description
            FROM Event
            WHERE Id = :eventId
        ];

        System.assertEquals('Square Booking BK-123 (LOC-1)', insertedEvent.Subject);
        System.assertEquals(Datetime.newInstanceGmt(2026, 1, 11, 17, 0, 0), insertedEvent.StartDateTime);
        System.assertEquals(Datetime.newInstanceGmt(2026, 1, 11, 17, 45, 0), insertedEvent.EndDateTime);
        System.assert(insertedEvent.Description.contains('Customer Id: CUST-1'));
    }

    @IsTest
    static void throwsWhenBookingIdMissing() {
        try {
            SquareAppointmentSync.createAppointmentFromSquare(null, UserInfo.getUserId());
            System.assert(false, 'Expected exception for missing booking id.');
        } catch (SquareAppointmentSync.SquareApiException e) {
            System.assert(e.getMessage().contains('bookingId is required'));
        }
    }
}
