import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const Tz = require("../timezone-utils.js");

test("1. Bulgaria (Europe/Sofia) in winter -> UTC+02:00 (120 mins), DST false", () => {
  const winter = new Date("2026-01-15T12:00:00Z");
  const info = Tz.getTimeZoneInfo("Bulgaria", winter);
  assert.equal(info.timeZone, "Europe/Sofia");
  assert.equal(info.offsetMinutes, 120);
  assert.equal(info.offsetFormatted, "UTC+02:00");
  assert.equal(info.offsetCompact, "UTC+2");
  assert.equal(info.isDST, false);
});

test("2. Bulgaria (Europe/Sofia) in summer -> UTC+03:00 (180 mins), DST true", () => {
  const summer = new Date("2026-07-15T12:00:00Z");
  const info = Tz.getTimeZoneInfo("Bulgaria", summer);
  assert.equal(info.timeZone, "Europe/Sofia");
  assert.equal(info.offsetMinutes, 180);
  assert.equal(info.offsetFormatted, "UTC+03:00");
  assert.equal(info.offsetCompact, "UTC+3");
  assert.equal(info.isDST, true);
});

test("3. India (Asia/Kolkata) year-round half-hour offset -> UTC+05:30 (330 mins)", () => {
  for (const iso of ["2026-01-15T00:00:00Z", "2026-07-15T00:00:00Z"]) {
    const info = Tz.getTimeZoneInfo("India", new Date(iso));
    assert.equal(info.timeZone, "Asia/Kolkata");
    assert.equal(info.offsetMinutes, 330);
    assert.equal(info.offsetFormatted, "UTC+05:30");
    assert.equal(info.offsetCompact, "UTC+5:30");
    assert.equal(info.isDST, false);
  }
});

test("4. Nepal (Asia/Kathmandu) quarter-hour offset -> UTC+05:45 (345 mins)", () => {
  const info = Tz.getTimeZoneInfo("Nepal", new Date("2026-03-10T10:00:00Z"));
  assert.equal(info.timeZone, "Asia/Kathmandu");
  assert.equal(info.offsetMinutes, 345);
  assert.equal(info.offsetFormatted, "UTC+05:45");
  assert.equal(info.offsetCompact, "UTC+5:45");
  assert.equal(info.isDST, false);
});

test("5. London (Europe/London) across standard (UTC+0) and DST (UTC+1)", () => {
  const winter = Tz.getTimeZoneInfo("London", new Date("2026-01-15T12:00:00Z"));
  const summer = Tz.getTimeZoneInfo("London", new Date("2026-07-15T12:00:00Z"));
  assert.equal(winter.offsetMinutes, 0);
  assert.equal(winter.offsetCompact, "UTC+0");
  assert.equal(winter.isDST, false);
  assert.equal(summer.offsetMinutes, 60);
  assert.equal(summer.offsetCompact, "UTC+1");
  assert.equal(summer.isDST, true);
});

test("6. Berlin (Europe/Berlin) across standard (UTC+1) and DST (UTC+2)", () => {
  const winter = Tz.getTimeZoneInfo("Berlin", new Date("2026-01-15T12:00:00Z"));
  const summer = Tz.getTimeZoneInfo("Berlin", new Date("2026-07-15T12:00:00Z"));
  assert.equal(winter.offsetMinutes, 60);
  assert.equal(winter.offsetCompact, "UTC+1");
  assert.equal(summer.offsetMinutes, 120);
  assert.equal(summer.offsetCompact, "UTC+2");
});

test("7. New York (America/New_York) negative offsets across standard (UTC-5) and DST (UTC-4)", () => {
  const winter = Tz.getTimeZoneInfo("New York", new Date("2026-01-15T12:00:00Z"));
  const summer = Tz.getTimeZoneInfo("New York", new Date("2026-07-15T12:00:00Z"));
  assert.equal(winter.offsetMinutes, -300);
  assert.equal(winter.offsetFormatted, "UTC-05:00");
  assert.equal(winter.offsetCompact, "UTC-5");
  assert.equal(summer.offsetMinutes, -240);
  assert.equal(summer.offsetFormatted, "UTC-04:00");
  assert.equal(summer.offsetCompact, "UTC-4");
});

test("8. Japan (Asia/Tokyo) year-round UTC+9 without DST", () => {
  const winter = Tz.getTimeZoneInfo("Japan", new Date("2026-01-15T12:00:00Z"));
  const summer = Tz.getTimeZoneInfo("Japan", new Date("2026-07-15T12:00:00Z"));
  assert.equal(winter.offsetMinutes, 540);
  assert.equal(summer.offsetMinutes, 540);
  assert.equal(summer.isDST, false);
});

test("9. Multiple timezones within a single country (USA & Australia)", () => {
  const instant = new Date("2026-01-15T12:00:00Z");
  const ny = Tz.getTimeZoneInfo("America/New_York", instant);
  const chicago = Tz.getTimeZoneInfo("America/Chicago", instant);
  const la = Tz.getTimeZoneInfo("America/Los_Angeles", instant);
  const perth = Tz.getTimeZoneInfo("Australia/Perth", instant);
  const eucla = Tz.getTimeZoneInfo("Australia/Eucla", instant);
  assert.equal(ny.offsetMinutes, -300);
  assert.equal(chicago.offsetMinutes, -360);
  assert.equal(la.offsetMinutes, -480);
  assert.equal(perth.offsetMinutes, 480);
  assert.equal(eucla.offsetMinutes, 525); // UTC+08:45
});

test("10. Date changes across midnight forward and backward", () => {
  const lateUtc = new Date("2026-07-15T22:30:00Z");
  const sofia = Tz.getTimeZoneInfo("Europe/Sofia", lateUtc);
  assert.equal(sofia.localDate, "2026-07-16");
  assert.equal(sofia.localTime, "01:30:00");

  const earlyUtc = new Date("2026-01-15T02:30:00Z");
  const ny = Tz.getTimeZoneInfo("America/New_York", earlyUtc);
  assert.equal(ny.localDate, "2026-01-14");
  assert.equal(ny.localTime, "21:30:00");
});

test("11. Invalid or missing timezone identifiers throw explicit errors", () => {
  assert.throws(() => Tz.getTimeZoneInfo(""), /Invalid or missing/);
  assert.throws(() => Tz.getTimeZoneInfo(null), /Invalid or missing/);
  assert.throws(() => Tz.getTimeZoneInfo("Invalid/NoSuchZone"), /Unrecognized/);
});

test("12. Exact DST transition boundary in Europe/Sofia (March 29, 2026 01:00 UTC)", () => {
  const beforeTransition = new Date("2026-03-29T00:59:00Z");
  const afterTransition = new Date("2026-03-29T01:01:00Z");
  assert.equal(Tz.getUtcOffsetMinutes("Europe/Sofia", beforeTransition), 120);
  assert.equal(Tz.getUtcOffsetMinutes("Europe/Sofia", afterTransition), 180);
});

test("13. Solar time is explicitly distinguished from civil timezone time", () => {
  const instant = new Date("2026-07-15T12:00:00Z");
  const sofiaCivil = Tz.getTimeZoneInfo("Europe/Sofia", instant);
  const sofiaSolar = Tz.getSolarTimeInfo(23.3219, instant);
  assert.equal(sofiaCivil.offsetMinutes, 180); // Legal civil time: UTC+3
  assert.equal(sofiaSolar.solarOffsetMinutes, 93); // Solar time at 23.32E: +1h 33m
  assert.match(sofiaSolar.solarOffsetFormatted, /Solar/);
});
