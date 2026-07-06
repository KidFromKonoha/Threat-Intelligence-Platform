const fs = require('fs');

fetch('http://localhost:8000/api/v1/openapi.json')
  .then(r => r.json())
  .then(data => {
    const inv = Object.keys(data.paths).filter(p => p.includes('investigation'));
    inv.forEach(p => {
      console.log(p);
      Object.keys(data.paths[p]).forEach(m => {
        console.log('  ' + m.toUpperCase());
        const d = data.paths[p][m];
        if (d.requestBody && d.requestBody.content) {
          const c = d.requestBody.content['application/json'];
          if (c && c.schema) {
            console.log('    Req Schema:', c.schema.$ref || Object.keys(c.schema.properties || {}).join(','));
          }
        }
        if (d.responses['200'] && d.responses['200'].content) {
          const c = d.responses['200'].content['application/json'];
          if (c && c.schema) {
            console.log('    Res Schema:', c.schema.$ref || (c.schema.items ? `Array of ${c.schema.items.$ref}` : Object.keys(c.schema.properties || {}).join(',')));
          }
        }
      });
    });
    
    // Output investigation related components
    console.log('\nComponents:');
    Object.keys(data.components.schemas).filter(k => k.includes('Investigation')).forEach(k => {
      console.log(k);
      console.log('  Props:', Object.keys(data.components.schemas[k].properties || {}).join(', '));
    });
  });
