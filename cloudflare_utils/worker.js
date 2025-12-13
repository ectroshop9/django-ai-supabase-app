export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // 1. رابط التحميل المحمي: /d/TOKEN
    if (path.startsWith('/d/')) {
      const token = path.split('/d/')[1];
      
      // ⭐ استخدم KV_BINDING الذي لديك ⭐
      const tokenData = await env.KV_BINDING.get(token, 'json');
      
      if (!tokenData) {
        return this.errorPage('الرابط غير صالح أو انتهت صلاحيته');
      }
      
      // التحقق من الصلاحية (ساعتين)
      const now = Date.now();
      if (now > tokenData.expires_at) {
        await env.KV_BINDING.delete(token);
        return this.errorPage('⏰ انتهت صلاحية الرابط (ساعتان)');
      }
      
      // التحقق من الاستخدام
      if (tokenData.used) {
        return this.errorPage('🔄 تم استخدام هذا الرابط مسبقاً');
      }
      
      // وضع علامة مستخدم
      tokenData.used = true;
      tokenData.used_at = now;
      tokenData.downloaded_ip = request.headers.get('CF-Connecting-IP');
      
      // حفظ لمدة 5 دقائق فقط بعد الاستخدام
      await env.KV_BINDING.put(token, JSON.stringify(tokenData), {
        expirationTtl: 300
      });
      
      // ⭐ توجيه إلى الملف الأصلي ⭐
      return Response.redirect(tokenData.file_url, 302);
    }
    
    // 2. API لتخزين التوكنات من Django
    if (path === '/_api/store' && request.method === 'POST') {
      // التحقق من السرية
      const apiKey = request.headers.get('X-API-Secret');
      if (apiKey !== env.API_SECRET) {
        return new Response('❌ غير مصرح', { status: 401 });
      }
      
      const data = await request.json();
      const { token, file_url } = data;
      
      // حساب وقت الانتهاء (ساعتين من الآن)
      const expires_at = Date.now() + (2 * 60 * 60 * 1000);
      
      const tokenData = {
        file_url: file_url,
        expires_at: expires_at,
        used: false,
        created_at: Date.now(),
        metadata: data.metadata || {}
      };
      
      // ⭐ تخزين في KV مع TTL تلقائي ⭐
      await env.KV_BINDING.put(
        token,
        JSON.stringify(tokenData),
        { expirationTtl: 7200 } // 7200 ثانية = ساعتين
      );
      
      return new Response(JSON.stringify({ 
        success: true,
        message: '✅ تم إنشاء الرابط المحمي',
        download_url: `${url.origin}/d/${token}`
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('🚀 خدمة التحميل المحمية نشطة', { status: 200 });
  },
  
  errorPage(message) {
    const html = `<!DOCTYPE html>
    <html dir="rtl">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>رابط التحميل</title>
      <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        .error { color: #dc3545; font-size: 20px; }
        .info { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }
      </style>
    </head>
    <body>
      <div class="error">${message}</div>
      <div class="info">
        <p>🔒 الرابط يعمل مرة واحدة فقط</p>
        <p>⏰ صلاحية الرابط: ساعتان</p>
        <p>📁 يمكنك طلب رابط جديد من مشترياتك</p>
      </div>
      <button onclick="window.close()">إغلاق</button>
    </body>
    </html>`;
    
    return new Response(html, {
      status: 410,
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }
};