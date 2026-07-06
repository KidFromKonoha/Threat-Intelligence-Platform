fetch('http://localhost:8000/api/v1/openapi.json')
  .then(r => r.json())
  .then(data => {
    const g = Object.keys(data.paths).filter(p => p.includes('graph'));
    g.forEach(p => {
      console.log(p);
      Object.keys(data.paths[p]).forEach(m => {
        console.log('  ' + m.toUpperCase());
        const d = data.paths[p][m];
        if (d.parameters) {
          d.parameters.forEach(par => console.log('    param:', par.name, par.in, 'required:', par.required));
        }
        if (d.responses['200'] && d.responses['200'].content) {
          const c = d.responses['200'].content['application/json'];
          if (c && c.schema) {
            const ref = c.schema.$ref;
            const items = c.schema.items && c.schema.items.$ref;
            console.log('    Res:', ref || items || JSON.stringify(c.schema).slice(0, 100));
          }
        }
      });
    });

    console.log('\nGraph Schemas:');
    Object.keys(data.components.schemas)
      .filter(k => k.toLowerCase().includes('graph'))
      .forEach(k => {
        const s = data.components.schemas[k];
        console.log('\n' + k);
        if (s.properties) {
          Object.keys(s.properties).forEach(prop => {
            const p = s.properties[prop];
            console.log('  ' + prop + ':', JSON.stringify(p).slice(0, 100));
          });
        } else {
          console.log('  ', JSON.stringify(s).slice(0, 200));
        }
      });
  });
