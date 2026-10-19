/**
 * Centralized IANA Timezone & Solar Time Utility
 * Resolves country/city/coordinate selections to canonical IANA timezones
 * and computes accurate date-specific UTC offsets (including DST, +05:30, +05:45).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.TimezoneUtils = factory();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const COUNTRY_TO_IANA = {
    "bulgaria": "Europe/Sofia",
    "bg": "Europe/Sofia",
    "bgr": "Europe/Sofia",
    "sofia": "Europe/Sofia",
    "india": "Asia/Kolkata",
    "in": "Asia/Kolkata",
    "ind": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "new delhi": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "bengaluru": "Asia/Kolkata",
    "nepal": "Asia/Kathmandu",
    "np": "Asia/Kathmandu",
    "npl": "Asia/Kathmandu",
    "kathmandu": "Asia/Kathmandu",
    "united kingdom": "Europe/London",
    "uk": "Europe/London",
    "gb": "Europe/London",
    "gbr": "Europe/London",
    "great britain": "Europe/London",
    "england": "Europe/London",
    "london": "Europe/London",
    "germany": "Europe/Berlin",
    "de": "Europe/Berlin",
    "deu": "Europe/Berlin",
    "berlin": "Europe/Berlin",
    "united states": "America/New_York",
    "united states of america": "America/New_York",
    "usa": "America/New_York",
    "us": "America/New_York",
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "denver": "America/Denver",
    "japan": "Asia/Tokyo",
    "jp": "Asia/Tokyo",
    "jpn": "Asia/Tokyo",
    "tokyo": "Asia/Tokyo",
    "australia": "Australia/Sydney",
    "au": "Australia/Sydney",
    "aus": "Australia/Sydney",
    "sydney": "Australia/Sydney",
    "perth": "Australia/Perth",
    "eucla": "Australia/Eucla",
    "adelaide": "Australia/Adelaide",
    "darwin": "Australia/Darwin",
    "france": "Europe/Paris",
    "paris": "Europe/Paris",
    "greece": "Europe/Athens",
    "athens": "Europe/Athens",
    "romania": "Europe/Bucharest",
    "bucharest": "Europe/Bucharest",
    "turkey": "Europe/Istanbul",
    "istanbul": "Europe/Istanbul",
    "china": "Asia/Shanghai",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "russia": "Europe/Moscow",
    "moscow": "Europe/Moscow",
    "brazil": "America/Sao_Paulo",
    "sao paulo": "America/Sao_Paulo",
    "canada": "America/Toronto",
    "toronto": "America/Toronto",
    "vancouver": "America/Vancouver",
    "newfoundland": "America/St_Johns",
    "st. john's": "America/St_Johns",
    "iran": "Asia/Tehran",
    "tehran": "Asia/Tehran",
    "afghanistan": "Asia/Kabul",
    "kabul": "Asia/Kabul",
    "myanmar": "Asia/Yangon",
    "yangon": "Asia/Yangon",
    "sri lanka": "Asia/Colombo",
    "colombo": "Asia/Colombo",
    "pakistan": "Asia/Karachi",
    "karachi": "Asia/Karachi",
    "bangladesh": "Asia/Dhaka",
    "dhaka": "Asia/Dhaka",
    "bhutan": "Asia/Thimphu",
    "united arab emirates": "Asia/Dubai",
    "uae": "Asia/Dubai",
    "dubai": "Asia/Dubai",
    "singapore": "Asia/Singapore",
    "new zealand": "Pacific/Auckland",
    "auckland": "Pacific/Auckland",
    "chatham": "Pacific/Chatham",
    "egypt": "Africa/Cairo",
    "cairo": "Africa/Cairo",
    "south africa": "Africa/Johannesburg",
    "johannesburg": "Africa/Johannesburg",
    "nigeria": "Africa/Lagos",
    "kenya": "Africa/Nairobi",
    "mexico": "America/Mexico_City",
    "argentina": "America/Argentina/Buenos_Aires",
    "chile": "America/Santiago",
    "utc": "UTC",
    "gmt": "UTC",
    "etc/utc": "UTC"
  };

  function isValidTimeZone(tz) {
    if (!tz || typeof tz !== "string") return false;
    try {
      Intl.DateTimeFormat(undefined, { timeZone: tz });
      return true;
    } catch (_) {
      return false;
    }
  }

  function resolveTimeZone(input) {
    if (!input || typeof input !== "string") {
      throw new Error("Invalid or missing location/timezone identifier.");
    }
    const trimmed = input.trim();
    if (!trimmed) {
      throw new Error("Empty location/timezone identifier.");
    }
    const key = trimmed.toLowerCase();
    if (COUNTRY_TO_IANA[key]) {
      return COUNTRY_TO_IANA[key];
    }
    if (isValidTimeZone(trimmed)) {
      return trimmed;
    }
    throw new Error('Unrecognized location or IANA timezone identifier: "' + trimmed + '"');
  }

  function getPartsInTimeZone(timeZone, date) {
    const d = date instanceof Date ? date : new Date(date);
    if (Number.isNaN(d.getTime())) {
      throw new Error("Invalid Date passed to timezone calculator.");
    }
    const validTz = resolveTimeZone(timeZone);
    const formatter = new Intl.DateTimeFormat("en-US", {
      timeZone: validTz,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hourCycle: "h23"
    });
    const parts = {};
    for (const part of formatter.formatToParts(d)) {
      if (part.type !== "literal") {
        parts[part.type] = parseInt(part.value, 10);
      }
    }
    return { parts, validTz, instant: d };
  }

  function getUtcOffsetMinutes(timeZone, date = new Date()) {
    const { parts, instant } = getPartsInTimeZone(timeZone, date);
    const asUTC = Date.UTC(
      parts.year,
      parts.month - 1,
      parts.day,
      parts.hour === 24 ? 0 : parts.hour,
      parts.minute,
      parts.second
    );
    const utcMidnightAdjusted = instant.getTime() - (instant.getTime() % 1000);
    return Math.round((asUTC - utcMidnightAdjusted) / 60000);
  }

  function formatUtcOffset(offsetMinutes, options = {}) {
    if (typeof offsetMinutes !== "number" || !Number.isFinite(offsetMinutes)) {
      throw new Error("Invalid offsetMinutes value.");
    }
    const compact = Boolean(options.compact);
    if (offsetMinutes === 0) {
      return compact ? "UTC+0" : "UTC+00:00";
    }
    const sign = offsetMinutes >= 0 ? "+" : "-";
    const abs = Math.abs(Math.round(offsetMinutes));
    const hours = Math.floor(abs / 60);
    const minutes = abs % 60;
    if (compact) {
      return minutes === 0
        ? "UTC" + sign + hours
        : "UTC" + sign + hours + ":" + String(minutes).padStart(2, "0");
    }
    return (
      "UTC" +
      sign +
      String(hours).padStart(2, "0") +
      ":" +
      String(minutes).padStart(2, "0")
    );
  }

  function isDstActive(timeZone, date = new Date()) {
    const { parts, validTz, instant } = getPartsInTimeZone(timeZone, date);
    const jan = new Date(Date.UTC(parts.year, 0, 15, 12, 0, 0));
    const jul = new Date(Date.UTC(parts.year, 6, 15, 12, 0, 0));
    const janOffset = getUtcOffsetMinutes(validTz, jan);
    const julOffset = getUtcOffsetMinutes(validTz, jul);
    if (janOffset === julOffset) return false;
    const currentOffset = getUtcOffsetMinutes(validTz, instant);
    const standardOffset = Math.min(janOffset, julOffset);
    return currentOffset !== standardOffset;
  }

  function getTimeZoneInfo(locationOrTz, date = new Date()) {
    const timeZone = resolveTimeZone(locationOrTz);
    const { parts, instant } = getPartsInTimeZone(timeZone, date);
    const offsetMinutes = getUtcOffsetMinutes(timeZone, instant);
    const dst = isDstActive(timeZone, instant);
    const localDate =
      String(parts.year).padStart(4, "0") +
      "-" +
      String(parts.month).padStart(2, "0") +
      "-" +
      String(parts.day).padStart(2, "0");
    const localTime =
      String(parts.hour === 24 ? 0 : parts.hour).padStart(2, "0") +
      ":" +
      String(parts.minute).padStart(2, "0") +
      ":" +
      String(parts.second).padStart(2, "0");

    return {
      input: locationOrTz,
      timeZone,
      offsetMinutes,
      offsetHours: offsetMinutes / 60,
      offsetFormatted: formatUtcOffset(offsetMinutes, { compact: false }),
      offsetCompact: formatUtcOffset(offsetMinutes, { compact: true }),
      isDST: dst,
      localDate,
      localTime,
      localDateTimeISO: localDate + "T" + localTime
    };
  }

  function getSolarTimeInfo(longitude, date = new Date()) {
    if (typeof longitude !== "number" || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
      throw new Error("Longitude must be a finite number between -180 and 180.");
    }
    const d = date instanceof Date ? date : new Date(date);
    const solarOffsetMinutes = Math.round(longitude * 4);
    const solarInstant = new Date(d.getTime() + solarOffsetMinutes * 60000);
    return {
      longitude,
      solarOffsetMinutes,
      solarOffsetFormatted: formatUtcOffset(solarOffsetMinutes, { compact: false }) + " (Solar)",
      solarTimeUTCReference: solarInstant.toISOString().slice(11, 19),
      label: "Theoretical Solar Time (distinct from legal civil timezone)"
    };
  }

  return {
    COUNTRY_TO_IANA,
    isValidTimeZone,
    resolveTimeZone,
    getUtcOffsetMinutes,
    formatUtcOffset,
    isDstActive,
    getTimeZoneInfo,
    getSolarTimeInfo
  };
});
