// UDAAN AI — reads the user's entered profile and turns it into the display
// model used by the Profile sheet. There are NO demo values: registration
// seeds a few identity fields, everything else is filled by the user in the
// Profile Builder and stored under "udaan_full_profile".

(function () {
  const PERSONA_LABEL = { students: "Student", farmers: "Farmer", jobseekers: "Job Seeker" };

  function normPersona(p) { return PERSONA_LABEL[p] ? p : "students"; }

  // Seed only the handful of fields captured at registration.
  function loadValues(persona) {
    var reg = {}, full = {};
    try { reg = JSON.parse(localStorage.getItem("udaan_profile") || "{}") || {}; } catch (e) {}
    try { full = JSON.parse(localStorage.getItem("udaan_full_profile") || "{}") || {}; } catch (e) {}
    var seed = {};
    ["full_name", "email", "mobile_number", "age", "date_of_birth", "gender",
      "state", "district", "pincode"].forEach(function (k) {
      if (reg[k]) seed[k] = reg[k];
    });
    return Object.assign({}, seed, full);
  }

  function isBuilt() {
    try { return localStorage.getItem("udaan_profile_built") === "1"; } catch (e) { return false; }
  }

  function saveValues(values) {
    try {
      localStorage.setItem("udaan_full_profile", JSON.stringify(values || {}));
      localStorage.setItem("udaan_profile_built", "1");
      
      var userId = localStorage.getItem("user_id");
      var role = localStorage.getItem("role") || window.__startPersona;
      
      if (role === "farmer" || role === "farmers") {
          var payload = {
              state: values.state,
              district: values.district,
              category: values.category,
              annual_income: values.annual_income || values.annual_family_income,
              owns_land: values.owns_land === "Yes",
              land_area: parseFloat(values.land_area || 0),
              land_unit: values.land_unit,
              crop_type: values.crop_type,
              farmer_registration: !!values.farmer_registration,
              pm_kisan_enrolled: !!values.pm_kisan_enrolled,
              crop_insurance: !!values.crop_insurance,
              smartphone: !!values.smartphone_available,
              internet_access: !!values.internet_access,
              documents: values.documents_available || []
          };

          fetch("http://localhost:8000/api/v1/profile/" + userId + "/farmer", {
              method: "PUT",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify(payload)
          }).then(function(res) {
              if (!res.ok) throw new Error("PUT profile failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/profile-context/generate", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({ user_id: userId })
              });
          }).then(function(res) {
              if (!res.ok) throw new Error("POST profile-context failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/ai-discovery/run", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({ user_id: userId })
              });
          }).then(function(res) {
              if (!res.ok) throw new Error("POST ai-discovery failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/eligibility/run", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({ user_id: userId })
              });
          }).then(function(res) {
              if (!res.ok) throw new Error("POST eligibility failed");
              return res.json();
          }).then(function() {
              location.hash = "#dashboard/farmers";
          }).catch(function(e) {
              console.error(e);
              location.hash = "#dashboard/farmers";
          });
      } else if (role === "student" || role === "students") {
          fetch("http://localhost:8000/api/v1/profile/" + userId + "/student", {
              method: "PUT",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify(values)
          }).then(function(res) {
              if (!res.ok) throw new Error("PUT profile failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/profile-context/generate", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({ user_id: userId })
              });
          }).then(function(res) {
              if (!res.ok) throw new Error("POST profile-context failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/ai-discovery/run", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({ user_id: userId })
              });
          }).then(function(res) {
              if (!res.ok) throw new Error("POST ai-discovery failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/eligibility/run", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({ user_id: userId })
              });
          }).then(function(res) {
              if (!res.ok) throw new Error("POST eligibility failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/readiness?user_id=" + userId);
          }).then(function(res) {
              if (!res.ok) throw new Error("GET readiness failed");
              return res.json();
          }).then(function() {
              return fetch("http://localhost:8000/api/v1/value?user_id=" + userId);
          }).then(function(res) {
              if (!res.ok) throw new Error("GET value failed");
              return res.json();
          }).then(function() {
              location.hash = "#dashboard/students";
          }).catch(function(e) {
              console.error(e);
              location.hash = "#dashboard/students";
          });
      }
    } catch (e) {}
  }

  function fmtDate(v) {
    try {
      var d = new Date(v);
      if (isNaN(d)) return v;
      return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
    } catch (e) { return v; }
  }

  function fieldValue(values, f) {
    var v = values[f.key];
    if (v === undefined || v === null || v === "") return "";
    if (f.type === "date") return fmtDate(v);
    return String(v);
  }

  // Count answered "units" for the completion score.
  function tally(sections, values, acc) {
    sections.forEach(function (s) {
      if (s.type === "multi") {
        acc.total += 1;
        if ((values[s.id] || []).length > 0) acc.filled += 1;
      } else if (s.type === "bool") {
        s.fields.forEach(function (f) {
          acc.total += 1;
          if (values[f.key] !== undefined) acc.filled += 1;
        });
      } else {
        s.fields.forEach(function (f) {
          acc.total += 1;
          if (fieldValue(values, f) !== "") acc.filled += 1;
        });
      }
    });
  }

  function buildSection(s, values) {
    if (s.type === "multi") {
      var sel = values[s.id] || [];
      return { title: s.title, icon: s.icon, type: "chips",
        items: s.options.map(function (o) { return { label: o, on: sel.indexOf(o) !== -1 }; }) };
    }
    if (s.type === "bool") {
      return { title: s.title, icon: s.icon, type: "status",
        items: s.fields.map(function (f) { return { label: f.label, on: !!values[f.key] }; }) };
    }
    return { title: s.title, icon: s.icon, type: "fields",
      fields: s.fields.map(function (f) { return { label: f.label, value: fieldValue(values, f) }; }) };
  }

  function buildFromValues(persona, values) {
    persona = normPersona(persona);
    var schema = window.UDAAN_PROFILE_SCHEMA;
    var sectionsSchema = schema.common.concat(schema.personas[persona] || []);

    var acc = { total: 0, filled: 0 };
    tally(sectionsSchema, values, acc);
    var completion = acc.total ? Math.round((acc.filled / acc.total) * 100) : 0;

    var docs = (values.documents_available || []).length;
    var totalDocs = (schema.common.find(function (s) { return s.id === "documents_available"; }) || { options: [] }).options.length;
    var interests = (values.interests || []).length;

    return {
      personaLabel: PERSONA_LABEL[persona],
      identity: {
        full_name: values.full_name || "",
        email: values.email || "",
        mobile_number: values.mobile_number || "",
        state: values.state || "",
      },
      completion: completion,
      fieldsFilled: acc.filled,
      fieldsTotal: acc.total,
      metrics: [
        { label: "Documents Ready", value: docs + "/" + totalDocs },
        { label: "Interests Chosen", value: String(interests) },
        { label: "Fields Completed", value: acc.filled + "/" + acc.total },
      ],
      sections: sectionsSchema.map(function (s) { return buildSection(s, values); }),
    };
  }

  window.UDAAN_LOAD_PROFILE = loadValues;
  window.UDAAN_SAVE_PROFILE = saveValues;
  window.UDAAN_PROFILE_BUILT = isBuilt;
  window.UDAAN_BUILD_FROM_VALUES = buildFromValues;
  window.UDAAN_BUILD_PROFILE = function (persona) { return buildFromValues(persona, loadValues(persona)); };
})();
