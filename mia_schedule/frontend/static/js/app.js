/**
 * MIA Schedule App - Main JavaScript
 */

class MIAScheduleApp {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'uk';
        this.currentTheme = localStorage.getItem('theme') || 'dark';

        // Правильно загружаем выбранную группу из localStorage
        const savedGroup = localStorage.getItem('selectedGroup');
        this.selectedGroup = savedGroup && savedGroup !== 'null' ? JSON.parse(savedGroup) : null;

        this.schedule = null;
        this.currentWeekIndex = 0;
        this.translations = {};

        this.init();
    }

    async init() {
        // Применяем тему сразу же
        this.applyTheme();

        // Load translations
        await this.loadTranslations();

        // Применяем язык сразу после загрузки переводов
        this.updateUILanguage();

        // Setup event listeners
        this.setupEventListeners();

        // Check if group is selected
        if (this.selectedGroup) {
            await this.loadSchedule();
            this.showScheduleScreen();
        } else {
            await this.loadGroupsStructure();
            this.showWelcomeScreen();
        }

        this.hideLoading();
    }

    setupEventListeners() {
        // Menu toggle
        document.getElementById('menu-toggle').addEventListener('click', () => this.toggleSidebar());
        document.getElementById('sidebar-close').addEventListener('click', () => this.toggleSidebar());
        document.getElementById('sidebar-overlay').addEventListener('click', () => this.toggleSidebar());

        // Sidebar buttons
        document.getElementById('btn-change-group').addEventListener('click', () => this.changeGroup());
        document.getElementById('btn-show-schedule').addEventListener('click', () => this.showSchedule());
        document.getElementById('btn-bell-schedule').addEventListener('click', () => this.showBellSchedule());
        document.getElementById('btn-language').addEventListener('click', () => this.showLanguageModal());
        document.getElementById('btn-theme').addEventListener('click', () => this.toggleTheme());
        document.getElementById('btn-developer-contacts').addEventListener('click', () => this.showContactsModal());

        // Install app button
        const btnInstall = document.getElementById('btn-install-app');
        if (btnInstall) {
            btnInstall.addEventListener('click', () => this.installApp());
        }

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => this.refreshSchedule());

        // Week navigation
        document.getElementById('btn-prev-week').addEventListener('click', () => this.previousWeek());
        document.getElementById('btn-next-week').addEventListener('click', () => this.nextWeek());

        // Welcome screen
        document.getElementById('select-faculty').addEventListener('change', (e) => this.onFacultyChange(e));
        document.getElementById('select-course').addEventListener('change', (e) => this.onCourseChange(e));
        document.getElementById('select-group').addEventListener('change', (e) => this.onGroupChange(e));
        document.getElementById('btn-save-group').addEventListener('click', () => this.saveGroup());

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.closeAllModals();
            });
        });

        document.querySelectorAll('.modal-overlay').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.closeAllModals();
            });
        });

        // Announcement button in lesson modal (event delegation)
        document.getElementById('lesson-modal').addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-show-ads');
            if (btn) {
                e.preventDefault();
                e.stopPropagation();
                const r1 = btn.dataset.r1;
                const r2 = btn.dataset.r2 || '';
                if (r1) this.showAnnouncementModal(r1, r2);
                return;
            }
        });

        // Announcement back button
        document.querySelector('.modal-back-btn').addEventListener('click', () => this.backToLessonModal());

        // Language options
        document.querySelectorAll('.language-option').forEach(el => {
            el.addEventListener('click', (e) => {
                const lang = el.dataset.lang;
                this.changeLanguage(lang);
            });
        });
    }

    async loadTranslations() {
        try {
            const response = await fetch(`/api/translations/${this.currentLang}`);
            const data = await response.json();
            if (data.success) {
                this.translations = data.data;
            }
        } catch (error) {
            console.error('Error loading translations:', error);
        }
    }

    async loadGroupsStructure() {
        try {
            const response = await fetch('/api/groups');
            const data = await response.json();
            if (data.success) {
                this.groupsStructure = data.data;
                this.populateFaculties();
            }
        } catch (error) {
            console.error('Error loading groups:', error);
        }
    }

    populateFaculties() {
        const select = document.getElementById('select-faculty');
        select.innerHTML = '<option value="">--Оберіть факультет--</option>';

        this.groupsStructure.forEach(faculty => {
            const option = document.createElement('option');
            option.value = faculty.faculty_id;
            option.textContent = faculty.faculty_name;
            option.dataset.facultyData = JSON.stringify(faculty);
            select.appendChild(option);
        });
    }

    onFacultyChange(e) {
        const select = e.target;
        const courseSelect = document.getElementById('select-course');
        const groupSelect = document.getElementById('select-group');

        courseSelect.innerHTML = '<option value="">--Оберіть курс--</option>';
        groupSelect.innerHTML = '<option value="">--Оберіть групу--</option>';
        courseSelect.disabled = true;
        groupSelect.disabled = true;
        document.getElementById('btn-save-group').disabled = true;

        if (select.value) {
            const option = select.options[select.selectedIndex];
            const faculty = JSON.parse(option.dataset.facultyData);

            faculty.courses.forEach(course => {
                const opt = document.createElement('option');
                opt.value = course.course_number;
                opt.textContent = `${course.course_number} курс`;
                opt.dataset.courseData = JSON.stringify(course);
                courseSelect.appendChild(opt);
            });

            courseSelect.disabled = false;
            this.selectedFaculty = faculty;
        }
    }

    onCourseChange(e) {
        const select = e.target;
        const groupSelect = document.getElementById('select-group');

        groupSelect.innerHTML = '<option value="">--Оберіть групу--</option>';
        groupSelect.disabled = true;
        document.getElementById('btn-save-group').disabled = true;

        if (select.value) {
            const option = select.options[select.selectedIndex];
            const course = JSON.parse(option.dataset.courseData);

            course.groups.forEach(group => {
                const opt = document.createElement('option');
                opt.value = group.group_id;
                opt.textContent = group.group_name;
                opt.dataset.groupData = JSON.stringify(group);
                groupSelect.appendChild(opt);
            });

            groupSelect.disabled = false;
            this.selectedCourse = course;
        }
    }

    onGroupChange(e) {
        const select = e.target;
        const btn = document.getElementById('btn-save-group');

        if (select.value) {
            const option = select.options[select.selectedIndex];
            const group = JSON.parse(option.dataset.groupData);

            this.tempGroup = {
                group_id: group.group_id,
                group_name: group.group_name,
                faculty_id: this.selectedFaculty.faculty_id,
                faculty_name: this.selectedFaculty.faculty_name,
                course: this.selectedCourse.course_number
            };

            btn.disabled = false;
        } else {
            btn.disabled = true;
        }
    }

    async saveGroup() {
        this.selectedGroup = this.tempGroup;
        localStorage.setItem('selectedGroup', JSON.stringify(this.selectedGroup));

        this.showLoading();
        await this.loadSchedule();
        this.showScheduleScreen();
        this.hideLoading();
    }

    async loadSchedule(forceRefresh = false) {
        try {
            const params = new URLSearchParams({
                faculty_id: this.selectedGroup.faculty_id,
                faculty_name: this.selectedGroup.faculty_name,
                course: this.selectedGroup.course,
                group_name: this.selectedGroup.group_name,
                force_refresh: forceRefresh
            });

            const response = await fetch(`/api/schedule/${this.selectedGroup.group_id}?${params}`);
            const data = await response.json();

            if (data.success) {
                this.schedule = data.data;
                this.currentWeekIndex = this.findCurrentWeek();
                this.renderSchedule();
            } else {
                alert('Помилка завантаження розкладу');
            }
        } catch (error) {
            console.error('Error loading schedule:', error);
            alert('Помилка мережі');
        }
    }

    findCurrentWeek() {
        if (!this.schedule || !this.schedule.weeks) return 0;

        const today = new Date().toISOString().split('T')[0];

        for (let i = 0; i < this.schedule.weeks.length; i++) {
            const week = this.schedule.weeks[i];
            if (week.week_start <= today && week.week_end >= today) {
                return i;
            }
        }

        return 0;
    }

    renderSchedule() {
        if (!this.schedule || this.currentWeekIndex >= this.schedule.weeks.length) {
            document.getElementById('empty-state').style.display = 'block';
            document.getElementById('schedule-content').innerHTML = '';
            return;
        }

        const week = this.schedule.weeks[this.currentWeekIndex];


        // Форматируем диапазон дат недели
        const dateRange = this.formatDateRange(week.week_start, week.week_end);
        document.getElementById('week-dates').textContent = dateRange;

        // Update navigation buttons
        document.getElementById('btn-prev-week').disabled = this.currentWeekIndex === 0;
        document.getElementById('btn-next-week').disabled = this.currentWeekIndex >= this.schedule.weeks.length - 1;

        // Render days
        const container = document.getElementById('schedule-content');
        container.innerHTML = '';

        if (!week.days || week.days.length === 0) {
            document.getElementById('empty-state').style.display = 'block';
            return;
        }

        document.getElementById('empty-state').style.display = 'none';

        week.days.forEach(day => {
            const dayCard = this.createDayCard(day);
            container.appendChild(dayCard);
        });
    }

    createDayCard(day) {
        const card = document.createElement('div');
        card.className = 'day-card';

        // Получаем название дня недели
        const dayDate = new Date(day.day_date);
        const locale = this.currentLang === 'uk' ? 'uk-UA' : 'en-GB';
        const dayName = dayDate.toLocaleDateString(locale, { weekday: 'long' });

        // Капитализируем первую букву
        const dayNameCapitalized = dayName.charAt(0).toUpperCase() + dayName.slice(1);

        const header = document.createElement('div');
        header.className = 'day-header';
        header.innerHTML = `
            <div class="day-name">${dayNameCapitalized}</div>
            <div class="day-date">${this.formatDate(day.day_date)}</div>
        `;
        card.appendChild(header);

        if (day.lessons && day.lessons.length > 0) {
            const lessonsContainer = document.createElement('div');
            lessonsContainer.className = 'day-lessons';

            day.lessons.forEach(lesson => {
                lesson.day_date = day.day_date;
                const lessonCard = this.createLessonCard(lesson);
                lessonsContainer.appendChild(lessonCard);
            });

            card.appendChild(lessonsContainer);
        }

        return card;
    }

    createLessonCard(lesson) {
        const card = document.createElement('div');
        card.className = `lesson-card type-${lesson.lesson_type}`;
        card.addEventListener('click', () => this.showLessonModal(lesson));

        const periodLabel = this.getLessonPeriodLabel(lesson.lesson_number);
        const bellIcon = lesson.announcement ? '<div class="lesson-announcement-indicator">🔔</div>' : '';

        card.innerHTML = `
            <div class="lesson-header-info">
                <div class="lesson-number">${periodLabel}</div>
                <div class="lesson-time">${lesson.start_time} - ${lesson.end_time}</div>
            </div>
            <div class="lesson-type-badge">${this.getLessonTypeText(lesson.lesson_type)}</div>
            <div class="lesson-subject">${lesson.subject}</div>
            <div class="lesson-room">${lesson.room || 'Аудиторія не вказана'}</div>
            <div class="lesson-info-icon">ℹ️</div>
            ${bellIcon}
        `;

        return card;
    }

    getLessonPeriodLabel(num) {
        if (this.currentLang === 'en') {
            const ordinals = ['th', 'st', 'nd', 'rd'];
            const v = num % 100;
            const suffix = ordinals[(v - 20) % 10] || ordinals[v] || ordinals[0];
            return `${num}${suffix} period`;
        }
        return `${num} пара`;
    }

    showLessonModal(lesson) {
        const modal = document.getElementById('lesson-modal');

        document.getElementById('modal-subject').textContent = lesson.subject;
        document.getElementById('modal-time').textContent = `${lesson.start_time} - ${lesson.end_time} (${this.getLessonPeriodLabel(lesson.lesson_number)})`;
        document.getElementById('modal-type').textContent = this.getLessonTypeText(lesson.lesson_type);
        document.getElementById('modal-room').textContent = lesson.room || 'не вказано';
        document.getElementById('modal-teacher').textContent = lesson.teacher_full || lesson.teacher || 'не вказано';

        // Показываем комментарий если есть
        if (lesson.notes) {
            document.getElementById('modal-notes').textContent = lesson.notes;
            document.getElementById('modal-notes-container').style.display = 'flex';
        } else {
            document.getElementById('modal-notes-container').style.display = 'none';
        }

        // Show/hide announcement button and set r1 value
        const adsBtn = modal.querySelector('.btn-show-ads');
        if (lesson.announcement && lesson.announcement.startsWith('ads:')) {
            adsBtn.dataset.r1 = lesson.announcement.slice(4);
            if (lesson.day_date) {
                const [y, m, d] = lesson.day_date.split('-');
                adsBtn.dataset.r2 = `${d}.${m}.${y}`;
            }
            adsBtn.textContent = this.translations.announcement || 'Оголошення';
            adsBtn.style.display = '';
        } else {
            adsBtn.style.display = 'none';
        }

        modal.classList.add('active');
        document.body.classList.add('modal-open');
    }


    async showAnnouncementModal(r1, r2) {
        const lessonModal = document.getElementById('lesson-modal');
        const announcementModal = document.getElementById('announcement-modal');
        const contentEl = document.getElementById('announcement-content');

        // Show loading state immediately
        contentEl.innerHTML = '<p class="announcement-loading">Завантаження...</p>';

        // Close lesson modal, open announcement modal with standard scale animation
        lessonModal.classList.remove('active');
        announcementModal.classList.add('active');

        // Fetch announcement HTML
        try {
            let url = `/api/announcement?r1=${encodeURIComponent(r1)}`;
            if (r2) url += `&r2=${encodeURIComponent(r2)}`;
            const response = await fetch(url);
            const data = await response.json();
            if (data.html) {
                contentEl.innerHTML = data.html;
                // Ensure all links open in a new tab (e.g. Teams links)
                contentEl.querySelectorAll('a').forEach(a => {
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                });
            } else {
                contentEl.textContent = data.error || (this.translations.error || 'Помилка завантаження');
            }
        } catch (error) {
            contentEl.textContent = this.translations.error || 'Помилка завантаження';
        }
    }

    backToLessonModal() {
        const lessonModal = document.getElementById('lesson-modal');
        const announcementModal = document.getElementById('announcement-modal');

        // Close announcement modal, re-open lesson modal with standard scale animation
        announcementModal.classList.remove('active');
        lessonModal.classList.add('active');
    }

    getLessonTypeText(type) {
        // Используем переводы если они загружены
        if (this.translations) {
            const types = {
                'lecture': this.translations.lecture || 'Лекція',
                'practice': this.translations.practice || 'Практика',
                'session': this.translations.session || 'Сесія',
                'exam': this.translations.exam || 'Екзамен',
                'consultation': this.translations.consultation || 'Консультація'
            };
            return types[type] || type;
        }

        // Fallback на украинский
        const types = {
            'lecture': 'Лекція',
            'practice': 'Практика',
            'session': 'Сесія',
            'exam': 'Екзамен',
            'consultation': 'Консультація'
        };
        return types[type] || type;
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        const locale = this.currentLang === 'uk' ? 'uk-UA' : 'en-GB';

        // Формат: "2 березня 2026" или "2 March 2026"
        return date.toLocaleDateString(locale, {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
    }

    formatDateRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const locale = this.currentLang === 'uk' ? 'uk-UA' : 'en-GB';

        // Формат: "2 березня 2026 - 8 березня 2026"
        const startStr = start.toLocaleDateString(locale, {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
        const endStr = end.toLocaleDateString(locale, {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });

        return `${startStr} - ${endStr}`;
    }

    async refreshSchedule() {
        this.showLoading();
        await this.loadSchedule(true);
        this.hideLoading();
    }

    previousWeek() {
        if (this.currentWeekIndex > 0) {
            this.currentWeekIndex--;
            this.renderSchedule();
        }
    }

    nextWeek() {
        if (this.currentWeekIndex < this.schedule.weeks.length - 1) {
            this.currentWeekIndex++;
            this.renderSchedule();
        }
    }

    toggleSidebar() {
        document.getElementById('sidebar').classList.toggle('open');
        document.getElementById('sidebar-overlay').classList.toggle('active');
        document.body.classList.toggle('modal-open');
    }

    changeGroup() {
        this.selectedGroup = null;
        localStorage.removeItem('selectedGroup');
        this.toggleSidebar();
        this.showWelcomeScreen();
        this.loadGroupsStructure();
    }

    showSchedule() {
        this.toggleSidebar();
        this.showScheduleScreen();
    }

    installApp() {
        this.toggleSidebar();
        if (window.deferredPrompt) {
            installPWA();
        } else {
            const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
            document.getElementById('ios-install-guide').style.display = isIOS ? 'block' : 'none';
            document.getElementById('generic-install-guide').style.display = isIOS ? 'none' : 'block';
            document.getElementById('install-guide-modal').classList.add('active');
            document.body.classList.add('modal-open');
        }
    }

    async showContactsModal() {
        const response = await fetch('/api/contacts');
        const data = await response.json();

        if (data.success) {
            document.getElementById('contact-github').href = data.data.github;
            document.getElementById('contact-telegram').href = data.data.telegram;
        }

        document.getElementById('contacts-modal').classList.add('active');
        this.toggleSidebar();
        document.body.classList.add('modal-open');
    }

    showLanguageModal() {
        document.querySelectorAll('.language-option').forEach(el => {
            el.classList.toggle('active', el.dataset.lang === this.currentLang);
        });
        document.getElementById('language-modal').classList.add('active');
        this.toggleSidebar();
        document.body.classList.add('modal-open');
    }

    async changeLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('language', lang);
        await this.loadTranslations();
        this.updateUILanguage();
        this.closeAllModals();

        // Перерисовать расписание с новым языком
        if (this.schedule) {
            this.renderSchedule();
        }
    }

    updateUILanguage() {
        const t = this.translations;

        // Обновляем заголовки
        document.querySelector('.app-title').textContent = t.app_name || 'SUTE Розклад';
        document.querySelector('#sidebar-title').textContent = t.app_name || 'SUTE Розклад';

        // Обновляем текст кнопок меню напрямую
        document.querySelector('#btn-change-group .sidebar-btn-text').textContent = t.change_group || 'Змінити групу';
        document.querySelector('#btn-show-schedule .sidebar-btn-text').textContent = t.show_schedule || 'Розклад занять';
        document.querySelector('#btn-bell-schedule .sidebar-btn-text').textContent = t.bell_schedule || 'Розклад дзвінків';

        // Обновляем дату в сайдбаре
        this.updateHeaderDate();

        // Обновляем название языка
        const langNames = {
            'uk': 'Українська',
            'en': 'English'
        };
        document.querySelector('#current-language').textContent = langNames[this.currentLang] || 'Українська';

        // Обновляем название темы
        this.updateThemeButton();

        // Обновляем кнопку контактов
        const contactBtn = document.querySelector('#btn-developer-contacts span');
        if (contactBtn) {
            contactBtn.textContent = t.developer_contacts || 'Контакти розробника';
        }

        // Обновляем кнопку установки
        const installBtn = document.getElementById('btn-install-app-text');
        if (installBtn) {
            installBtn.textContent = t.download_app || 'Завантажити';
        }

        // Обновляем welcome screen
        const welcomeTitle = document.querySelector('.welcome-title');
        if (welcomeTitle) welcomeTitle.textContent = t.welcome || 'Ласкаво просимо!';

        const welcomeText = document.querySelector('.welcome-text');
        if (welcomeText) welcomeText.textContent = t.welcome_text || 'Оберіть свою групу для відображення розкладу';

        // Обновляем bell schedule screen
        const bellHeading = document.getElementById('bell-schedule-heading');
        if (bellHeading) bellHeading.textContent = t.bell_schedule || 'Розклад дзвінків';

        const bellColPeriod = document.getElementById('bell-col-period');
        if (bellColPeriod) bellColPeriod.textContent = t.lesson_number || 'Пара';

        const bellColTime = document.getElementById('bell-col-time');
        if (bellColTime) bellColTime.textContent = t.time || 'Час';

        // Обновляем метки пар в bell schedule
        for (let i = 1; i <= 6; i++) {
            const el = document.getElementById(`bell-period-${i}`);
            if (el) el.textContent = this.getLessonPeriodLabel(i);
        }

        // Обновляем модальные окна заголовки
        const modalTitles = document.querySelectorAll('.modal-title');
        if (modalTitles[0]) modalTitles[0].textContent = t.lesson_info || 'Інформація про пару';
        if (modalTitles[1]) modalTitles[1].textContent = t.announcement || 'Оголошення';
        if (modalTitles[2]) modalTitles[2].textContent = t.developer_contacts || 'Контакти розробника';
        if (modalTitles[3]) modalTitles[3].textContent = t.language || 'Мова';
        if (modalTitles[4]) modalTitles[4].textContent = t.add_to_homescreen || 'Додати на робочий стіл';

        // Оновлюємо текст кнопки оголошення у lesson-modal
        const adsBtn = document.querySelector('.btn-show-ads');
        if (adsBtn) adsBtn.textContent = t.announcement || 'Оголошення';

        // Находим labels в модальном окне lesson-modal
        const lessonModal = document.getElementById('lesson-modal');
        if (lessonModal) {
            const labels = lessonModal.querySelectorAll('.lesson-detail-label');
            if (labels[0]) labels[0].textContent = t.subject || 'Предмет';
            if (labels[1]) labels[1].textContent = t.time || 'Час';
            if (labels[2]) labels[2].textContent = t.type || 'Тип';
            if (labels[3]) labels[3].textContent = t.room || 'Аудиторія';
            if (labels[4]) labels[4].textContent = t.teacher || 'Викладач';
            if (labels[5]) labels[5].textContent = t.notes || 'Коментар';
        }

        // Обновляем тексты загрузки
        const loadingText = document.querySelector('.loading-text');
        if (loadingText) loadingText.textContent = t.loading || 'Завантаження...';

        // Обновляем empty state
        const emptyStateTitle = document.querySelector('.empty-state h3');
        if (emptyStateTitle) emptyStateTitle.textContent = t.no_lessons || 'Немає занять';

        // Обновляем шаги инструкции установки
        const iosStep1 = document.getElementById('ios-step-1');
        if (iosStep1) iosStep1.textContent = t.ios_step_1 || 'Натисніть кнопку «Поділитися» (кнопка Share) внизу браузера';
        const iosStep2 = document.getElementById('ios-step-2');
        if (iosStep2) iosStep2.textContent = t.ios_step_2 || 'Оберіть «Додати на домашній екран»';
        const iosStep3 = document.getElementById('ios-step-3');
        if (iosStep3) iosStep3.textContent = t.ios_step_3 || 'Натисніть «Встановити як веб-додаток» та підтвердіть встановлення';
        const genericStep1 = document.getElementById('generic-step-1');
        if (genericStep1) genericStep1.textContent = t.ios_step_1 || 'Натисніть кнопку «Поділитися» (кнопка Share) внизу браузера';
        const genericStep2 = document.getElementById('generic-step-2');
        if (genericStep2) genericStep2.textContent = t.ios_step_2 || 'Оберіть «Додати на домашній екран»';
        const genericStep3 = document.getElementById('generic-step-3');
        if (genericStep3) genericStep3.textContent = t.ios_step_3 || 'Натисніть «Встановити як веб-додаток» та підтвердіть встановлення';
    }

    updateHeaderDate() {
        const el = document.getElementById('header-date');
        if (!el) return;
        const now = new Date();
        const locale = this.currentLang === 'uk' ? 'uk-UA' : 'en-GB';
        el.textContent = now.toLocaleDateString(locale, {
            day: '2-digit',
            month: 'long',
            year: 'numeric'
        });
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.classList.remove('modal-open');
    }

    applyTheme() {
        if (this.currentTheme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
        this.updateThemeButton();
    }

    updateThemeButton() {
        const t = this.translations;
        const themeBtn = document.querySelector('#current-theme');

        if (this.currentTheme === 'light') {
            if (themeBtn) {
                const themeName = this.currentLang === 'uk' ? 'Світла тема' : 'Light theme';
                themeBtn.textContent = themeName;
            }
        } else {
            if (themeBtn) {
                const themeName = this.currentLang === 'uk' ? 'Темна тема' : 'Dark theme';
                themeBtn.textContent = themeName;
            }
        }
    }

    showWelcomeScreen() {
        document.getElementById('welcome-screen').style.display = 'flex';
        document.getElementById('schedule-screen').style.display = 'none';
        document.getElementById('bell-schedule-screen').style.display = 'none';
    }

    showScheduleScreen() {
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('schedule-screen').style.display = 'block';
        document.getElementById('bell-schedule-screen').style.display = 'none';
    }

    showBellSchedule() {
        this.toggleSidebar();
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('schedule-screen').style.display = 'none';
        document.getElementById('bell-schedule-screen').style.display = 'block';
    }

    showLoading() {
        document.getElementById('loading-spinner').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-spinner').classList.add('hidden');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MIAScheduleApp();
});

