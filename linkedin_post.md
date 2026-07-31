# Post LinkedIn - devctl

Lors de mon stage PFA, j'ai constaté la répétition constante de certaines tâches chronophages dans le quotidien de développement. Il fallait systématiquement ouvrir plusieurs terminaux pour démarrer chaque service manuellement, gérer l'environnement backend, lancer le serveur de développement frontend et initialiser la base de données.

Initialement, j'ai conçu un outil simple pour centraliser et automatiser ce processus de lancement. Au fil du projet, l'outil a évolué pour répondre à d'autres besoins récurrents :

1. La génération automatique de templates CRUD (Entities, DTOs, Controllers, Services) pour accélérer le développement des tranches verticales backend et frontend.
2. L'intégration et l'automatisation de la conteneurisation Docker (génération de Dockerfiles multi-stages et de fichiers docker-compose).
3. La mise en place d'un tableau de bord TUI (Terminal User Interface) pour superviser l'état des services, consulter les logs et suivre la consommation des ressources système en temps réel.

C'est ainsi qu'est né **devctl**, une solution CLI d'orchestration multi-stack et daemon-less.

---

**Fonctionnalités principales de devctl :**

- **Orchestration unifiée (`devctl run`) :** Détection automatique du projet et lancement simultané des bases de données et des services avec streaming de logs centralisé.
- **Scaffolding full-stack (`devctl init`) :** Initialisation rapide de projets backend (Spring Boot, NestJS, FastAPI, Go, Django) et frontend (Angular, React, Vue, NextJS, Svelte).
- **Génération de ressources (`devctl add resource`) :** Création simultanée du code boilerplate sur les couches backend et frontend.
- **Dashboard TUI (`devctl tui`) :** Interface interactive pour suivre la consommation processeur, mémoire et disque tout en gérant les processus.
- **Support Docker automatique :** Génération à chaud de Dockerfiles optimisés et de fichiers Compose pour la production.
- **Architecture native :** Exécution sans daemon d'arrière-plan sur Linux, macOS et Windows, préservant les ressources système et l'environnement hôte.

---

Le projet est accessible en open-source sur GitHub :  
[https://github.com/yss-ef/devctl](https://github.com/yss-ef/devctl)

![Aperçu du TUI devctl](file:///home/youssef/Projects/Personal/Apps/devctl/devctl_tui_screenshot.png)

N'hésitez pas à consulter le dépôt et à partager vos retours.

#SoftwareEngineering #DevOps #Python #OpenSource #FullStack #DeveloperTools #CLI #CleanArchitecture #Docker
