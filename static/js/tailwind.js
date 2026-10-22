//tailwind
const shop = document.querySelector('#shop');
const menu = document.querySelector('#menu');
const billing = document.querySelector('#billing');
const billingTab = document.querySelector('#billingTab');
const history = document.querySelector('#history');
const historyTab = document.querySelector('#historyTab');
const library = document.querySelector('#library');
const libraryTab = document.querySelector('#libraryTab');
const preference = document.querySelector('#preference');
const preferenceTab = document.querySelector('#preferenceTab');

shop.addEventListener('click',()=>{
    if (menu.classList.contains('hidden')){
        menu.classList.remove('hidden');
    }else{
        menu.classList.add('hidden');
    }
})

billing.addEventListener('click',()=>{
    if(history.classList.contains('font-bold') && history.classList.contains('text-black')){
        history.classList.remove('font-bold');
        history.classList.remove('text-black');
    }else if(library.classList.contains('font-bold') && library.classList.contains('text-black')){
        library.classList.remove('font-bold');
        library.classList.remove('text-black');
    }else if(preference.classList.contains('font-bold') && preference.classList.contains('text-black')){
        preference.classList.remove('font-bold');
        preference.classList.remove('text-black');
    }else if(admin.classList.contains('font-bold') && admin.classList.contains('text-black')){
        admin.classList.remove('font-bold');
        admin.classList.remove('text-black');
    }

    if(historyTab.classList.contains('hidden')!==true){
        historyTab.classList.add('hidden');
    }else if(libraryTab.classList.contains('hidden')!==true){
        libraryTab.classList.add('hidden');
    }else if(preferenceTab.classList.contains('hidden')!==true){
        preferenceTab.classList.add('hidden');
    }else if(adminTab.classList.contains('hidden')!==true){
        adminTab.classList.add('hidden');
    }

    if (billing.classList.contains('font-bold') && billing.classList.contains('text-black')){
        billing.classList.remove('font-bold');
        billing.classList.remove('text-black');
    }else{
       billing.classList.add('font-bold');
       billing.classList.add('text-black');
    }
    
    if (billingTab.classList.contains('hidden')){
        billingTab.classList.remove('hidden');
    }else{
        billingTab.classList.add('hidden');
    }
})

history.addEventListener('click',()=>{
    if(billing.classList.contains('font-bold') && billing.classList.contains('text-black')){
        billing.classList.remove('font-bold');
        billing.classList.remove('text-black');
    }else if(library.classList.contains('font-bold') && library.classList.contains('text-black')){
        library.classList.remove('font-bold');
        library.classList.remove('text-black');
    }else if(preference.classList.contains('font-bold') && preference.classList.contains('text-black')){
        preference.classList.remove('font-bold');
        preference.classList.remove('text-black');
    }else if(admin.classList.contains('font-bold') && admin.classList.contains('text-black')){
        admin.classList.remove('font-bold');
        admin.classList.remove('text-black');
    }

    if(billingTab.classList.contains('hidden')!==true){
        billingTab.classList.add('hidden');
    }else if(libraryTab.classList.contains('hidden')!==true){
        libraryTab.classList.add('hidden');
    }else if(preferenceTab.classList.contains('hidden')!==true){
        preferenceTab.classList.add('hidden');
    }else if(adminTab.classList.contains('hidden')!==true){
        adminTab.classList.add('hidden');
    }

    if (history.classList.contains('font-bold') && history.classList.contains('text-black')){
        history.classList.remove('font-bold');
        history.classList.remove('text-black');
    }else{
        history.classList.add('font-bold');
        history.classList.add('text-black');
    }

    if (historyTab.classList.contains('hidden')){
        historyTab.classList.remove('hidden');
    }else{
        historyTab.classList.add('hidden');
    }
})


library.addEventListener('click',()=>{
    if(billing.classList.contains('font-bold') && billing.classList.contains('text-black')){
        billing.classList.remove('font-bold');
        billing.classList.remove('text-black');
    }else if(history.classList.contains('font-bold') && history.classList.contains('text-black')){
        history.classList.remove('font-bold');
        history.classList.remove('text-black');
    }else if(preference.classList.contains('font-bold') && preference.classList.contains('text-black')){
        preference.classList.remove('font-bold');
        preference.classList.remove('text-black');
    }else if(admin.classList.contains('font-bold') && admin.classList.contains('text-black')){
        admin.classList.remove('font-bold');
        admin.classList.remove('text-black');
    }

    if(billingTab.classList.contains('hidden')!==true){
        billingTab.classList.add('hidden');
    }else if(historyTab.classList.contains('hidden')!==true){
        historyTab.classList.add('hidden');
    }else if(preferenceTab.classList.contains('hidden')!==true){
        preferenceTab.classList.add('hidden');
    }else if(adminTab.classList.contains('hidden')!==true){
        adminTab.classList.add('hidden');
    }

    if (library.classList.contains('font-bold') && library.classList.contains('text-black')){
        library.classList.remove('font-bold');
        library.classList.remove('text-black');
    }else{
        library.classList.add('font-bold');
        library.classList.add('text-black');
    }

    if (libraryTab.classList.contains('hidden')){
        libraryTab.classList.remove('hidden');
    }else{
        libraryTab.classList.add('hidden');
    }
})

preference.addEventListener('click',()=>{
    if(billing.classList.contains('font-bold') && billing.classList.contains('text-black')){
        billing.classList.remove('font-bold');
        billing.classList.remove('text-black');
    }else if(history.classList.contains('font-bold') && history.classList.contains('text-black')){
        history.classList.remove('font-bold');
        history.classList.remove('text-black');
    }else if(library.classList.contains('font-bold') && library.classList.contains('text-black')){
        library.classList.remove('font-bold');
        library.classList.remove('text-black');
    }else if(admin.classList.contains('font-bold') && admin.classList.contains('text-black')){
        admin.classList.remove('font-bold');
        admin.classList.remove('text-black');
    }

    if(billingTab.classList.contains('hidden')!==true){
        billingTab.classList.add('hidden');
    }else if(historyTab.classList.contains('hidden')!==true){
        historyTab.classList.add('hidden');
    }else if(libraryTab.classList.contains('hidden')!==true){
        libraryTab.classList.add('hidden');
    }else if(adminTab.classList.contains('hidden')!==true){
        adminTab.classList.add('hidden');
    }

    if (preference.classList.contains('font-bold') && preference.classList.contains('text-black')){
        preference.classList.remove('font-bold');
        preference.classList.remove('text-black');
    }else{
        preference.classList.add('font-bold');
        preference.classList.add('text-black');
    }

    if (preferenceTab.classList.contains('hidden')){
        preferenceTab.classList.remove('hidden');
    }else{
        preferenceTab.classList.add('hidden');
    }
})


admin.addEventListener('click',()=>{
    if(billing.classList.contains('font-bold') && billing.classList.contains('text-black')){
        billing.classList.remove('font-bold');
        billing.classList.remove('text-black');
    }else if(history.classList.contains('font-bold') && history.classList.contains('text-black')){
        history.classList.remove('font-bold');
        history.classList.remove('text-black');
    }else if(library.classList.contains('font-bold') && library.classList.contains('text-black')){
        library.classList.remove('font-bold');
        library.classList.remove('text-black');
    }else if(preference.classList.contains('font-bold') && preference.classList.contains('text-black')){
        preference.classList.remove('font-bold');
        preference.classList.remove('text-black');
    }

    if(billingTab.classList.contains('hidden')!==true){
        billingTab.classList.add('hidden');
    }else if(historyTab.classList.contains('hidden')!==true){
        historyTab.classList.add('hidden');
    }else if(preferenceTab.classList.contains('hidden')!==true){
        preferenceTab.classList.add('hidden');
    }else if(libraryTab.classList.contains('hidden')!==true){
        libraryTab.classList.add('hidden');
    }

    if (admin.classList.contains('font-bold') && admin.classList.contains('text-black')){
        admin.classList.remove('font-bold');
        admin.classList.remove('text-black');
    }else{
        admin.classList.add('font-bold');
        admin.classList.add('text-black');
    }

    if (adminTab.classList.contains('hidden')){
        adminTab.classList.remove('hidden');
    }else{
        adminTab.classList.add('hidden');
    }
})